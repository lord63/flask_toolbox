#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import datetime

from lxml import html


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
    def issues(self):
        return self._get_num('.counter', 0)

    @property
    def pull_requests(self):
        return self._get_num('.counter', -1)
