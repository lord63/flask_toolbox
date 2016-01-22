#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask_toolbox.web.extensions import db


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.Text)
    packages = db.relationship('Package', backref='category', lazy='dynamic')


class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    name = db.Column(db.String(40))
    description = db.Column(db.Text)
    website = db.Column(db.String(80))
    documentation = db.Column(db.String(80))
    source_code = db.Column(db.String(80))
    bug_tracker = db.Column(db.String(80))
    pypi_info = db.relationship('PyPI', backref='package')
    github_info = db.relationship('Github', backref='package')


class PyPI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'))


class Github(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'))
