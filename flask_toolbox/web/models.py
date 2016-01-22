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
    website_url = db.Column(db.String(80))
    documentation_url = db.Column(db.String(80))
    source_code_url = db.Column(db.String(80))
    bug_tracker_url = db.Column(db.String(80))
    pypi_info = db.relationship('PyPI', backref='package')
    github_info = db.relationship('Github', backref='package')

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


class Github(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'))
