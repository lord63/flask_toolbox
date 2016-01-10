#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import


class PyPI(object):
    def __init__(self, name):
        self.name = name

    @property
    def download_num(self):
        """The total download num of current version."""
        pass

    @property
    def release_num(self):
        """The total release num of the package."""
        pass

    @property
    def current_version(self):
        """The current version num for the package."""
        pass

    @property
    def released_date(self):
        """The release date of the current version for the package."""
        pass

    @property
    def first_release(self):
        """The time when the first release of the package."""
        pass

    @property
    def python_version(self):
        """The supported python versions for the package"""
        pass
