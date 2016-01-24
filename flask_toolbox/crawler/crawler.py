#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import requests

from flask_toolbox.crawler.pypi import PyPI


class Crawler(object):
    def __init__(self, name):
        self.name = name

    def get_pypi_info(self):
        package_url = 'https://pypi.python.org/pypi/{0}/json'.format(self.name)
        response = requests.get(package_url)
        package_info = PyPI(self.name, response.json())
        return package_info

    def get_github_info(self):
        pass
