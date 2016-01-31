#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import datetime
import re


class PyPIMeta(object):
    def __init__(self, response):
        self.response = response

    @property
    def download_num(self):
        """The total download num of current version."""
        return sum(release['downloads'] for release in self.response['urls'])

    @property
    def release_num(self):
        """The total release num of the package."""
        return len(self.response['releases'])

    @property
    def current_version(self):
        """The current version num for the package."""
        return self.response['info']['version']

    @property
    def released_date(self):
        """The release date of the current version for the package."""
        # Please note that I take the first item's upload_time in the
        # releaselist as the released_date.
        return self._parse_date(self.response['urls'][0]['upload_time'])

    @property
    def first_release(self):
        """The time when the first release of the package."""
        # We need to filter those releases that the value is a empty
        # list. Or we can't sort the releases. E.g. the requests
        # library's v0.0.1 release is a empty list('0.0.1': []).
        first = sorted(
            [item for item in self.response['releases'].items() if item[1]],
            key=lambda x: x[1][0].get('upload_time')
        )[0]
        return self._parse_date(first[1][0]['upload_time'])

    @property
    def python_version(self):
        """The supported python versions for the package"""
        versions = [
            item.split('::')[-1].strip()
            for item in self.response['info']['classifiers']
            if 'Programming Language' in item and
            len(item.split('::')[-1].strip())==3]
        return ' '.join(versions)

    def _parse_date(self, date_string):
        """Parse the date string and return the datetime object."""
        return datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')
