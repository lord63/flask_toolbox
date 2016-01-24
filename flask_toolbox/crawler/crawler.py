#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import requests

from flask_toolbox.crawler.pypi import PyPIMeta


class Crawler(object):
    def get_pypi_info(self, url):
        response = requests.get('{0}/json'.format(url))
        package_info = PyPIMeta(response.json())
        return package_info

    def get_github_info(self):
        pass
