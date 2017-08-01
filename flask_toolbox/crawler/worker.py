#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import time

from flask_toolbox.extensions import db
from flask_toolbox.models import PyPI, Github, Package
from flask_toolbox.crawler.crawler import Crawler
from flask_toolbox.crawler.github import (get_first_commit,
                                          get_development_activity)


def update_pypi_info():
    for package in Package.query.all():
        time.sleep(0.3)
        update_package_pypi_info(package.id)


def update_package_pypi_info(package_id):
    package = Package.query.get(package_id)
    package_info = Crawler().get_pypi_info(package.pypi_url)
    pypi = PyPI.query.filter_by(package_id=package.id).first()
    if pypi:
        pypi.download_num = package_info.download_num
        pypi.release_num = package_info.release_num
        pypi.current_version = package_info.current_version
        pypi.released_date = package_info.released_date
        pypi.first_release = package_info.first_release
        pypi.python_version = package_info.python_version
        db.session.add(pypi)
        db.session.commit()
    else:
        new_pypi = PyPI(
            package_id=package.id,
            download_num=package_info.download_num,
            release_num=package_info.release_num,
            current_version=package_info.current_version,
            released_date=package_info.released_date,
            first_release=package_info.first_release,
            python_version=package_info.python_version
        )
        db.session.add(new_pypi)
        db.session.commit()


def update_github_info():
    for package in Package.query.all():
        time.sleep(0.3)
        update_package_github_info(package.id)


def update_package_github_info(package_id):
    package = Package.query.get(package_id)
    repo_info = Crawler().get_github_info(package.source_code_url)
    github = Github.query.filter_by(package_id=package.id).first()
    if github:
        github.watchers = repo_info.watchers
        github.forks = repo_info.forks
        github.last_commit = repo_info.last_commit
        github.contributors = repo_info.contributors
        github.issues = repo_info.issues
        github.pull_requests = repo_info.pull_requests
        github.development_activity = get_development_activity(
            package.source_code_url)
        db.session.add(github)
        db.session.commit()
    else:
        new_github = Github(
            package_id=package.id,
            watchers=repo_info.watchers,
            forks=repo_info.forks,
            last_commit=repo_info.last_commit,
            contributors=repo_info.contributors,
            issues=repo_info.issues,
            pull_requests=repo_info.pull_requests,
            development_activity=get_development_activity(
                package.source_code_url),
            first_commit=get_first_commit(
                package.source_code_url, repo_info.commits)
        )
        db.session.add(new_github)
        db.session.commit()
