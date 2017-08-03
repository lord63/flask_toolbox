#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import datetime
from functools import partial
import math
import os

from lxml import html
import requests


# Use your github token if you want a higher API rate limit.
if os.environ.get('GITHUB_TOKEN'):
    api_request = partial(requests.get, headers={
        'User-Agent': 'https://github.com/lord63/flask_toolbox',
        'Authorization': 'token {0}'.format(os.environ['GITHUB_TOKEN'])})
else:
    api_request = partial(requests.get, headers={
        'User-Agent': 'https://github.com/lord63/flask_toolbox'})


class GithubMeta(object):
    def __init__(self, response, url):
        self.tree = html.fromstring(response.text)
        self.url = url

    def _custom_int(self, string_number):
        # 1999 commits will be 1,999 commits on github.
        if ',' in string_number:
            return int(string_number.replace(',', ''))
        return int(string_number)

    def _get_num(self, css_expression, index):
        result = self.tree.cssselect(css_expression)[index].text
        if result is None:
            return result
        else:
            return self._custom_int(result.strip())

    @property
    def watchers(self):
        return self._get_num('.social-count', 1)

    @property
    def forks(self):
        return self._get_num('.social-count', -1)

    @property
    def last_commit(self):
        commit_time = self.tree.cssselect('relative-time')[0].get('datetime')
        return _parse_date(commit_time)

    @property
    def contributors(self):
        num = self._get_num('.text-emphasized', -1)
        # You may get None for contributor num, see #17.
        # This patch is not elegant enough, please help me improve it.
        if num is None:
            owner, repo = self.url.split('/')[-2:]
            url = 'https://api.github.com/repos/{0}/{1}/contributors'.format(
                owner, repo)
            response = api_request(url)
            return len(response.json())
        else:
            return num

    @property
    def commits(self):
        return self._get_num('.text-emphasized', 0)

    @property
    def issues(self):
        return self._get_num('.Counter', 0)

    @property
    def pull_requests(self):
        return self._get_num('.Counter', 1)


def get_first_commit(url, commit_num):
    # Steal this idea from https://github.com/wong2/first-commit.
    first_commit_page = int(math.ceil(commit_num / 35))
    page_url = "{0}/commits?page={1}".format(url, first_commit_page)
    tree = html.fromstring(requests.get(page_url).text)
    first_commit_time = tree.cssselect('relative-time')[-1].get('datetime')
    return _parse_date(first_commit_time)


def get_development_activity(url):
    owner, repo = url.split('/')[-2:]
    url = 'https://api.github.com/repos/{0}/{1}/commits'.format(owner, repo)
    response = api_request(url)
    epoch = datetime.datetime.utcfromtimestamp(0)
    deltas = [_parse_date(commit['commit']['committer']['date']) - epoch
              for commit in response.json()]
    average_delta = (
        sum(delta.total_seconds() for delta in deltas) // len(response.json()))
    average_date = epoch + datetime.timedelta(seconds=average_delta)
    delta_of_day = (datetime.datetime.now() - average_date).days
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
