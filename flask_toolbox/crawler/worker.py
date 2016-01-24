#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask_toolbox.web.app import create_app
from flask_toolbox.web.configs import Config
from flask_toolbox.web.extensions import db
from flask_toolbox.web.models import PyPI, Github
from flask_toolbox.crawler.crawler import Crawler


class Worker(object):
    def __init__(self):
        app = create_app(Config)
        app.app_context().push()

    def update_package_pypi_info(self):
        for pypi in PyPI.query.all():
            pakcage_info = Crawler(pypi.package.name).get_pypi_info()
            pypi.download_num = pakcage_info.download_num
            pypi.release_num = pakcage_info.release_num
            pypi.current_version = pakcage_info.current_version
            pypi.released_date = pakcage_info.released_date
            pypi.first_release = pakcage_info.first_release
            pypi.python_version = pakcage_info.python_version
            db.session.add(pypi)
            db.session.commit()

    def update_package_github_info(self):
        pass
