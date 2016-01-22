#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import Flask
from flask_admin import Admin
from flask_admin.contrib import sqla

from flask_toolbox.web.extensions import db
from flask_toolbox.web.models import Category, Package


def create_app(config):
    app = Flask('flask_toolbox')
    app.config.from_object(config)

    db.init_app(app)

    admin = Admin()
    admin.add_view(sqla.ModelView(Category, db.session))
    admin.add_view(sqla.ModelView(Package, db.session))
    admin.init_app(app)

    return app
