from datetime import datetime, timezone

from flask_toolbox.package_audit import (
    audit_packages,
    get_github_repo,
    get_latest_release,
    get_package_status,
    load_packages_file,
    render_text_report,
    summarize_results,
)


def test_get_github_repo_parses_standard_url():
    assert get_github_repo('https://github.com/pallets/flask') == ('pallets', 'flask')


def test_get_github_repo_strips_git_suffix():
    assert get_github_repo('https://github.com/pallets/flask.git') == ('pallets', 'flask')


def test_get_github_repo_returns_none_for_non_github():
    assert get_github_repo('https://gitlab.com/foo/bar') is None


def test_get_latest_release():
    payload = {
        'releases': {
            '0.1': [{'upload_time': '2020-01-01T00:00:00'}],
            '1.0': [{'upload_time': '2024-06-15T12:00:00'}],
            '0.5': [],
        }
    }
    assert get_latest_release(payload) == '2024-06-15T12:00:00'


def test_get_latest_release_empty():
    assert get_latest_release({'releases': {}}) is None


def test_get_package_status():
    data = {'package_status': {'unmaintained': ['A', 'B'], 'archived': None}}
    result = get_package_status(data)
    assert result == {'unmaintained': {'A', 'B'}, 'archived': set()}


def test_get_package_status_missing():
    assert get_package_status({}) == {}


def test_load_packages_file(tmp_path):
    f = tmp_path / 'test.yml'
    f.write_text('packages:\n  Flask:\n    pypi_url: https://pypi.org/project/Flask/\n',
                 encoding='utf-8')
    data = load_packages_file(str(f))
    assert 'Flask' in data['packages']


def test_audit_packages_uses_github_api():
    """Verify audit_packages calls GitHub REST API, not HTML scraping."""
    requested_urls = []

    class FakeResponse:
        status_code = 200
        ok = True
        url = 'https://pypi.org/project/Flask/'

        def __init__(self, payload=None):
            self._payload = payload or {}

        def json(self):
            return self._payload

    class FakeSession:
        headers = {}

        def get(self, url, **kwargs):
            requested_urls.append(url)
            if 'api.github.com' in url:
                return FakeResponse({
                    'html_url': 'https://github.com/pallets/flask',
                    'archived': False,
                    'pushed_at': '2024-06-01T00:00:00Z',
                })
            if 'pypi' in url:
                return FakeResponse({
                    'releases': {'1.0': [{'upload_time': '2024-01-01T00:00:00'}]},
                })
            return FakeResponse()

    packages = {
        'Flask': {
            'pypi_url': 'https://pypi.org/project/Flask/',
            'source_code_url': 'https://github.com/pallets/flask',
        }
    }

    results = audit_packages(packages, session=FakeSession())

    assert len(results) == 1
    github_urls = [u for u in requested_urls if 'github' in u]
    assert any('api.github.com/repos/' in u for u in github_urls)
    # Should NOT fetch HTML from github.com directly
    assert not any(u == 'https://github.com/pallets/flask' for u in requested_urls)
    assert results[0].get('github_archived') is False
    assert results[0].get('github_last_commit') == '2024-06-01T00:00:00Z'


def test_summarize_results_flags_failures():
    now = datetime(2026, 4, 4, tzinfo=timezone.utc)
    results = [
        {
            'name': 'DeadSource',
            'pypi_status': 200,
            'github_status': 404,
            'source_code_url': 'https://github.com/example/dead-source',
        },
        {
            'name': 'MovedRepo',
            'pypi_status': 200,
            'github_status': 200,
            'source_code_url': 'https://github.com/example/old-repo',
            'github_final_url': 'https://github.com/example/new-repo',
            'github_archived': False,
            'github_last_commit': '2026-04-01T00:00:00Z',
        },
        {
            'name': 'ArchivedPackage',
            'pypi_status': 200,
            'github_status': 200,
            'source_code_url': 'https://github.com/example/archived',
            'github_final_url': 'https://github.com/example/archived',
            'github_archived': True,
        },
        {
            'name': 'StalePackage',
            'pypi_status': 200,
            'github_status': 200,
            'source_code_url': 'https://github.com/example/stale',
            'github_final_url': 'https://github.com/example/stale',
            'github_archived': False,
            'github_last_commit': '2020-01-01T00:00:00Z',
        },
    ]

    summary = summarize_results(results, {}, stale_years=3, now=now)

    assert summary['dead_source'] == ['DeadSource']
    assert summary['archived'] == ['ArchivedPackage']
    assert summary['unmaintained'] == ['StalePackage']
    assert summary['redirected_source'][0]['name'] == 'MovedRepo'
    assert summary['has_failures'] is True


def test_summarize_results_accepts_marked_packages():
    now = datetime(2026, 4, 4, tzinfo=timezone.utc)
    results = [
        {
            'name': 'StalePackage',
            'pypi_status': 200,
            'github_status': 200,
            'source_code_url': 'https://github.com/example/stale',
            'github_final_url': 'https://github.com/example/stale',
            'github_archived': False,
            'github_last_commit': '2020-01-01T00:00:00Z',
        },
    ]

    summary = summarize_results(
        results,
        {'unmaintained': {'StalePackage', 'MissingPackage'}},
        stale_years=3,
        now=now,
    )

    assert summary['unmaintained'] == []
    assert summary['marked_unmaintained'] == ['StalePackage']
    assert summary['unknown_status_packages'] == ['MissingPackage']
    assert summary['has_failures'] is True


def test_render_text_report():
    summary = {
        'package_count': 2,
        'dead_pypi': ['DeadPkg'],
        'dead_source': [],
        'redirected_source': [],
        'archived': [],
        'unmaintained': [],
        'marked_archived': [],
        'marked_unmaintained': ['OldPkg'],
        'unknown_status_packages': [],
        'has_failures': True,
    }
    report = render_text_report(summary)
    assert 'Packages checked: 2' in report
    assert 'DeadPkg' in report
    assert 'Marked unmaintained packages: 1' in report
