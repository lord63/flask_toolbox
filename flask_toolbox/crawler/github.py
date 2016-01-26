#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import datetime
import math

from lxml import html
import requests


class GithubMeta(object):
    def __init__(self, response):
        self.tree = html.fromstring(response.text)

    def _custom_int(self, string_number):
        # 1999 commits will be 1,999 commits on github.
        if ',' in string_number:
            return int(string_number.replace(',', ''))
        return int(string_number)

    def _get_num(self, css_expression, index):
        number = self._custom_int(
            self.tree.cssselect(css_expression)[index].text.strip())
        return number

    @property
    def watchers(self):
        return self._get_num('.social-count', 0)

    @property
    def forks(self):
        return self._get_num('.social-count', -1)

    @property
    def last_commit(self):
        commit_time = self.tree.cssselect('time')[0].get('datetime')
        return _parse_date(commit_time)

    @property
    def contributors(self):
        return self._get_num('.text-emphasized', -1)

    @property
    def commits(self):
        return self._get_num('.text-emphasized', 0)

    @property
    def issues(self):
        return self._get_num('.counter', 0)

    @property
    def pull_requests(self):
        return self._get_num('.counter', -1)


def get_first_commit(url):
    # Steal this idea from https://github.com/wong2/first-commit.
    commits = GithubMeta(requests.get(url)).commits
    first_commit_page = int(math.ceil(commits / 35))
    page_url = "{0}/commits?page={1}".format(url, first_commit_page)
    tree = html.fromstring(requests.get(page_url).text)
    first_commit_time = tree.cssselect('time')[-1].get('datetime')
    return _parse_date(first_commit_time)


def get_development_activity(url):
    owner, repo = url.split('/')[-2:]
    url = 'https://api.github.com/repos/{0}/{1}/commits'.format(owner, repo)
    response = requests.get(url)
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
