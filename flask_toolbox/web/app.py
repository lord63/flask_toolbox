#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import Flask

from flask_admin.contrib.sqla import ModelView

from flask_toolbox.web.extensions import db, admin
from flask_toolbox.web.models import Category, Package, PyPI, Github
from flask_toolbox.web.admin import CategoryView, PackageView


admin.add_view(CategoryView(Category, db.session))
admin.add_view(PackageView(Package, db.session))
admin.add_view(ModelView(PyPI, db.session))
admin.add_view(ModelView(Github, db.session))


def create_app(config):
    app = Flask('flask_toolbox')
    app.config.from_object(config)

    db.init_app(app)
    admin.init_app(app)

    return app
