import datetime
from functools import partial
import os
from urllib.parse import parse_qs, urlparse

import requests


# Use your github token if you want a higher API rate limit.
_api_headers = {
    'Accept': 'application/vnd.github+json',
    'User-Agent': 'https://github.com/lord63/flask_toolbox',
}
if os.environ.get('GITHUB_TOKEN'):
    _api_headers['Authorization'] = 'Bearer {0}'.format(
        os.environ['GITHUB_TOKEN'])

api_request = partial(requests.get, headers=_api_headers)
API_ROOT = 'https://api.github.com'


class GithubMeta:
    def __init__(self, url):
        self.url = url
        self.owner, self.repo = _parse_repo_url(url)
        self._repo_data = None
        self._commits_response = None
        self._commits_data = None
        self._contributors = None
        self._pull_requests = None

    def _ensure_repo_data(self):
        if self._repo_data is None:
            self._repo_data = _request(
                '{0}/repos/{1}/{2}'.format(API_ROOT, self.owner, self.repo)
            ).json()

    def _ensure_commits_data(self):
        if self._commits_response is None:
            self._commits_response = _request(
                '{0}/repos/{1}/{2}/commits'.format(
                    API_ROOT, self.owner, self.repo),
                params={'per_page': 1}
            )
            self._commits_data = self._commits_response.json()

    @property
    def watchers(self):
        self._ensure_repo_data()
        return self._repo_data['watchers_count']

    @property
    def forks(self):
        self._ensure_repo_data()
        return self._repo_data['forks_count']

    @property
    def archived(self):
        self._ensure_repo_data()
        return self._repo_data.get('archived', False)

    @property
    def last_commit(self):
        self._ensure_commits_data()
        commit_time = self._commits_data[0]['commit']['committer']['date']
        return _parse_date(commit_time)

    @property
    def contributors(self):
        if self._contributors is None:
            self._contributors = _get_count(
                '{0}/repos/{1}/{2}/contributors'.format(
                    API_ROOT, self.owner, self.repo),
                params={'anon': 1, 'per_page': 1}
            )
        return self._contributors

    @property
    def commits(self):
        self._ensure_commits_data()
        return _get_last_page(self._commits_response, self._commits_data)

    @property
    def issues(self):
        self._ensure_repo_data()
        return max(self._repo_data['open_issues_count'] - self.pull_requests, 0)

    @property
    def pull_requests(self):
        if self._pull_requests is None:
            self._pull_requests = _get_count(
                '{0}/repos/{1}/{2}/pulls'.format(
                    API_ROOT, self.owner, self.repo),
                params={'state': 'open', 'per_page': 1}
            )
        return self._pull_requests


def get_first_commit(url, commit_num):
    owner, repo = _parse_repo_url(url)
    if not commit_num:
        return None

    response = _request(
        '{0}/repos/{1}/{2}/commits'.format(API_ROOT, owner, repo),
        params={'page': commit_num, 'per_page': 1}
    )
    first_commit_time = response.json()[0]['commit']['committer']['date']
    return _parse_date(first_commit_time)


def get_development_activity(url):
    owner, repo = _parse_repo_url(url)
    response = _request(
        '{0}/repos/{1}/{2}/commits'.format(API_ROOT, owner, repo),
        params={'per_page': 100}
    )
    commits = response.json()
    if not commits:
        return 'Inactive'

    epoch = datetime.datetime(1970, 1, 1)
    deltas = [_parse_date(commit['commit']['committer']['date']) - epoch
              for commit in commits]
    average_delta = (
        sum(delta.total_seconds() for delta in deltas) // len(commits))
    average_date = epoch + datetime.timedelta(seconds=average_delta)
    delta_of_day = (
        datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        - average_date).days
    if 0 <= delta_of_day <= 7:
        return 'Very active'
    elif 8 <= delta_of_day <= 31:
        return 'Active'
    elif 32 <= delta_of_day <= 365:
        return 'Less Active'
    else:
        return 'Inactive'


def _parse_date(date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')


def _parse_repo_url(url):
    path = urlparse(url).path.strip('/').split('/')
    owner, repo = path[:2]
    if repo.endswith('.git'):
        repo = repo[:-4]
    return owner, repo


def _request(url, **kwargs):
    response = api_request(url, **kwargs)
    response.raise_for_status()
    return response


def _get_count(url, params):
    response = _request(url, params=params)
    return _get_last_page(response, response.json())


def _get_last_page(response, payload):
    last_link = response.links.get('last')
    if last_link:
        query = parse_qs(urlparse(last_link['url']).query)
        page_values = query.get('page')
        if page_values:
            return int(page_values[0])

    # When there is no pagination (e.g. only 1 contributor), the full
    # result set fits in a single page, so its length is the total count.
    if isinstance(payload, list):
        return len(payload)

    return 0
