#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask_toolbox.web.extensions import db


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.Text)
    packages = db.relationship('Package', backref='category', lazy='dynamic')

    def __repr__(self):
        return '<Category %r>' % self.name


class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    name = db.Column(db.String(40))
    description = db.Column(db.Text)
    pypi_url = db.Column(db.String(80))
    documentation_url = db.Column(db.String(80))
    source_code_url = db.Column(db.String(80))
    bug_tracker_url = db.Column(db.String(80))
    pypi_info = db.relationship('PyPI', uselist=False, backref='package')
    github_info = db.relationship('Github', uselist=False, backref='package')

    def __repr__(self):
        return '<Package %r>' % self.name


class PyPI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'))
    download_num = db.Column(db.Integer)
    release_num = db.Column(db.Integer)
    current_version = db.Column(db.String(20))
    released_date = db.Column(db.DateTime)
    first_release = db.Column(db.DateTime)
    python_version = db.Column(db.String(40))

    def __repr__(self):
        return '<PyPI %r>' % self.package.name


class Github(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'))
    watchers = db.Column(db.Integer)
    forks = db.Column(db.Integer)
    development_activity = db.Column(db.String(20))
    last_commit = db.Column(db.DateTime)
    first_commit = db.Column(db.DateTime)
    contributors = db.Column(db.Integer)
    issues = db.Column(db.Integer)
    pull_requests = db.Column(db.Integer)

    def __repr__(self):
        return '<Github %r>' % self.package.name
