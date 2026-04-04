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
    def __init__(self, response_or_url, url=None):
        if url is None:
            self.url = response_or_url
        else:
            self.url = url

        owner, repo = _parse_repo_url(self.url)
        self.owner = owner
        self.repo = repo
        self.repo_data = _request(
            '{0}/repos/{1}/{2}'.format(API_ROOT, owner, repo)
        ).json()
        self.commits_response = _request(
            '{0}/repos/{1}/{2}/commits'.format(API_ROOT, owner, repo),
            params={'per_page': 1}
        )
        self.commits_data = self.commits_response.json()
        self._contributors = None
        self._pull_requests = None

    @property
    def watchers(self):
        return self.repo_data['watchers_count']

    @property
    def forks(self):
        return self.repo_data['forks_count']

    @property
    def last_commit(self):
        commit_time = self.commits_data[0]['commit']['committer']['date']
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
        return _get_last_page(self.commits_response, self.commits_data)

    @property
    def issues(self):
        return max(self.repo_data['open_issues_count'] - self.pull_requests, 0)

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

    epoch = datetime.datetime.fromtimestamp(
        0, datetime.timezone.utc).replace(tzinfo=None)
    deltas = [_parse_date(commit['commit']['committer']['date']) - epoch
              for commit in commits]
    average_delta = (
        sum(delta.total_seconds() for delta in deltas) // len(commits))
    average_date = epoch + datetime.timedelta(seconds=average_delta)
    delta_of_day = (
        datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        - average_date).days
    if delta_of_day in range(0, 7+1):
        return 'Very active'
    elif delta_of_day in range(8, 31+1):
        return 'Active'
    elif delta_of_day in range(32, 365+1):
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
    if hasattr(response, 'raise_for_status'):
        response.raise_for_status()
    return response


def _get_count(url, params):
    response = _request(url, params=params)
    return _get_last_page(response, response.json())


def _get_last_page(response, payload):
    last_link = response.links.get('last')
    if last_link:
        query = parse_qs(urlparse(last_link['url']).query)
        return int(query['page'][0])

    if isinstance(payload, list):
        return len(payload)

    return 0
