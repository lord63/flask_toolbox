#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask_toolbox.web.app import create_app
from flask_toolbox.web.configs import Config
from flask_toolbox.web.extensions import db
from flask_toolbox.web.models import PyPI, Github, Package
from flask_toolbox.crawler.crawler import Crawler


class Worker(object):
    def __init__(self):
        app = create_app(Config)
        app.app_context().push()

    def update_package_pypi_info(self):
        for package in Package.query.all():
            pakcage_info = Crawler().get_pypi_info(package.pypi_url)
            pypi = PyPI.query.filter_by(package_id=package.id).first()
            if pypi:
                pypi.download_num = pakcage_info.download_num
                pypi.release_num = pakcage_info.release_num
                pypi.current_version = pakcage_info.current_version
                pypi.released_date = pakcage_info.released_date
                pypi.first_release = pakcage_info.first_release
                pypi.python_version = pakcage_info.python_version
                db.session.add(pypi)
                db.session.commit()
            else:
                new_pypi = PyPI(
                    package_id = package.id,
                    download_num = pakcage_info.download_num,
                    release_num = pakcage_info.release_num,
                    current_version = pakcage_info.current_version,
                    released_date = pakcage_info.released_date,
                    first_release = pakcage_info.first_release,
                    python_version = pakcage_info.python_version
                )
                db.session.add(new_pypi)
                db.session.commit()

    def update_package_github_info(self):
        pass
