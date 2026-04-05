import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import requests
import yaml


DEFAULT_STALE_YEARS = 3.0
DEFAULT_TIMEOUT = 20


def get_default_packages_path():
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
        'packages.yml',
    )


def load_packages_file(path=None):
    path = path or get_default_packages_path()
    with open(path, encoding='utf-8') as package_file:
        return yaml.safe_load(package_file)


def get_package_status(data):
    status = data.get('package_status') or {}
    return {name: set(values or []) for name, values in status.items()}


def get_github_repo(url):
    parsed = urlparse(url)
    if 'github.com' not in parsed.netloc:
        return None

    parts = [part for part in parsed.path.split('/') if part]
    if len(parts) < 2:
        return None

    return parts[0], parts[1].replace('.git', '')


def get_pypi_json_url(url):
    parsed = urlparse(url)
    parts = [part for part in parsed.path.split('/') if part]

    if parsed.netloc == 'pypi.org' and len(parts) >= 2 and parts[0] == 'project':
        return 'https://pypi.org/pypi/{0}/json'.format(parts[1])

    return '{0}/json'.format(url.rstrip('/'))


def get_latest_release(payload):
    release_dates = []
    for files in (payload.get('releases') or {}).values():
        for release_file in files:
            release_time = (release_file.get('upload_time_iso_8601') or
                            release_file.get('upload_time'))
            if release_time:
                release_dates.append(release_time)

    if not release_dates:
        return None

    return max(release_dates)


def _github_api_headers():
    headers = {
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'flask-toolbox-package-audit',
    }
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer {0}'.format(token)
    return headers


def audit_packages(packages, session=None, timeout=DEFAULT_TIMEOUT):
    session = session or requests.Session()
    session.headers.setdefault('User-Agent', 'flask-toolbox-package-audit')
    github_headers = _github_api_headers()
    results = []

    for package_name, package_info in packages.items():
        result = {
            'name': package_name,
            'pypi_url': package_info['pypi_url'],
            'source_code_url': package_info['source_code_url'],
        }

        try:
            pypi_response = session.get(
                get_pypi_json_url(package_info['pypi_url']), timeout=timeout)
            result['pypi_status'] = pypi_response.status_code
            result['pypi_final_url'] = pypi_response.url
            if pypi_response.ok:
                result['pypi_last_release'] = get_latest_release(pypi_response.json())
        except requests.RequestException as exc:
            result['pypi_error'] = str(exc)

        github_repo = get_github_repo(package_info['source_code_url'])
        if github_repo:
            owner, repository = github_repo
            api_url = 'https://api.github.com/repos/{0}/{1}'.format(
                owner, repository)

            try:
                api_response = session.get(
                    api_url, headers=github_headers, timeout=timeout)
                result['github_status'] = api_response.status_code
                if api_response.ok:
                    repo_data = api_response.json()
                    html_url = repo_data.get('html_url', '').rstrip('/')
                    result['github_final_url'] = html_url
                    result['github_archived'] = repo_data.get('archived', False)
                    pushed_at = repo_data.get('pushed_at')
                    if pushed_at:
                        result['github_last_commit'] = pushed_at
                else:
                    result['github_final_url'] = 'https://github.com/{0}/{1}'.format(
                        owner, repository)
            except requests.RequestException as exc:
                result['github_error'] = str(exc)

        results.append(result)

    return results


def get_stale_before(now, stale_years):
    return now - timedelta(days=int(stale_years * 365.25))


def summarize_results(results, package_status, stale_years=DEFAULT_STALE_YEARS, now=None):
    now = now or datetime.now(timezone.utc)
    package_names = set(result['name'] for result in results)
    package_status = package_status or {}
    archived_markers = package_status.get('archived', set())
    unmaintained_markers = package_status.get('unmaintained', set())
    stale_before = get_stale_before(now, stale_years)

    summary = {
        'package_count': len(results),
        'dead_pypi': [],
        'dead_source': [],
        'redirected_source': [],
        'archived': [],
        'unmaintained': [],
        'marked_archived': [],
        'marked_unmaintained': [],
        'unknown_status_packages': sorted((archived_markers | unmaintained_markers) - package_names),
    }

    for result in results:
        if result.get('pypi_status') == 404:
            summary['dead_pypi'].append(result['name'])

        if result.get('github_status') == 404:
            summary['dead_source'].append(result['name'])
            continue

        if (result.get('github_final_url') and
                result['github_final_url'].rstrip('/') != result['source_code_url'].rstrip('/')):
            summary['redirected_source'].append({
                'name': result['name'],
                'current_url': result['source_code_url'],
                'final_url': result['github_final_url'],
            })

        if result.get('github_archived'):
            if result['name'] in archived_markers:
                summary['marked_archived'].append(result['name'])
            else:
                summary['archived'].append(result['name'])
            continue

        last_commit = result.get('github_last_commit')
        if not last_commit:
            continue

        last_commit_datetime = datetime.fromisoformat(last_commit.replace('Z', '+00:00'))
        if last_commit_datetime <= stale_before:
            if result['name'] in unmaintained_markers:
                summary['marked_unmaintained'].append(result['name'])
            else:
                summary['unmaintained'].append(result['name'])

    summary['has_failures'] = any((
        summary['dead_pypi'],
        summary['dead_source'],
        summary['redirected_source'],
        summary['archived'],
        summary['unmaintained'],
        summary['unknown_status_packages'],
    ))
    return summary


def audit_packages_file(path=None, stale_years=DEFAULT_STALE_YEARS, timeout=DEFAULT_TIMEOUT,
                        session=None, now=None):
    data = load_packages_file(path)
    results = audit_packages(data['packages'], session=session, timeout=timeout)
    summary = summarize_results(
        results,
        get_package_status(data),
        stale_years=stale_years,
        now=now,
    )
    return results, summary


def _format_package_list(items):
    if not items:
        return '  (none)'
    return '\n'.join('  - {0}'.format(item) for item in items)


def _format_redirects(items):
    if not items:
        return '  (none)'
    return '\n'.join(
        '  - {0}: {1} -> {2}'.format(item['name'], item['current_url'], item['final_url'])
        for item in items
    )


def render_text_report(summary, stale_years=DEFAULT_STALE_YEARS):
    lines = [
        'Package audit summary',
        '=====================',
        'Packages checked: {0}'.format(summary['package_count']),
        'Dead PyPI URLs: {0}'.format(len(summary['dead_pypi'])),
        'Dead source URLs: {0}'.format(len(summary['dead_source'])),
        'Source URL redirects to update: {0}'.format(len(summary['redirected_source'])),
        'Archived packages needing cleanup: {0}'.format(len(summary['archived'])),
        'Unmaintained packages needing cleanup (> {0:g} years): {1}'.format(
            stale_years,
            len(summary['unmaintained']),
        ),
        'Marked archived packages: {0}'.format(len(summary['marked_archived'])),
        'Marked unmaintained packages: {0}'.format(len(summary['marked_unmaintained'])),
        'Unknown package_status entries: {0}'.format(len(summary['unknown_status_packages'])),
        '',
        'Dead PyPI URLs:',
        _format_package_list(summary['dead_pypi']),
        '',
        'Dead source URLs:',
        _format_package_list(summary['dead_source']),
        '',
        'Source URL redirects:',
        _format_redirects(summary['redirected_source']),
        '',
        'Archived packages needing cleanup:',
        _format_package_list(summary['archived']),
        '',
        'Unmaintained packages needing cleanup:',
        _format_package_list(summary['unmaintained']),
    ]

    if summary['unknown_status_packages']:
        lines.extend([
            '',
            'Unknown package_status entries:',
            _format_package_list(summary['unknown_status_packages']),
        ])

    return '\n'.join(lines)


def build_argument_parser():
    parser = argparse.ArgumentParser(
        description='Audit packages.yml for dead links and stale projects.')
    parser.add_argument('packages_file', nargs='?', default=get_default_packages_path())
    parser.add_argument('--stale-years', default=DEFAULT_STALE_YEARS, type=float)
    parser.add_argument('--timeout', default=DEFAULT_TIMEOUT, type=int)
    parser.add_argument('--json', action='store_true', dest='json_output')
    return parser


def main(argv=None):
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    results, summary = audit_packages_file(
        path=args.packages_file,
        stale_years=args.stale_years,
        timeout=args.timeout,
    )

    if args.json_output:
        print(json.dumps({'results': results, 'summary': summary}, indent=2, sort_keys=True))
    else:
        print(render_text_report(summary, stale_years=args.stale_years))

    return 1 if summary['has_failures'] else 0


if __name__ == '__main__':
    sys.exit(main())
