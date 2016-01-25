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

    def _get_num(self, css_expression, index):
        return int(self.tree.cssselect(css_expression)[index].text.strip())

    @property
    def watchers(self):
        return self._get_num('.social-count', 0)

    @property
    def forks(self):
        return self._get_num('.social-count', -1)

    @property
    def last_commit(self):
        commit_time = self.tree.cssselect('time')[0].get('datetime')
        return datetime.datetime.strptime(commit_time, '%Y-%m-%dT%H:%M:%SZ')

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
    return datetime.datetime.strptime(first_commit_time, '%Y-%m-%dT%H:%M:%SZ')
