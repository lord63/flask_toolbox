#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import Flask
from werkzeug.utils import import_string

from flask_toolbox.web.extensions import db, admin
from flask_toolbox.web.models import Category, Package, PyPI, Github
from flask_toolbox.web.admin import (CategoryView, PackageView, PyPIView,
                                     GithubView)

blueprints = [
    'flask_toolbox.web.views.home:home_page',
    'flask_toolbox.web.views.category:category_page',
    'flask_toolbox.web.views.categories:categories_page',
    'flask_toolbox.web.views.package:package_page',
    'flask_toolbox.web.views.packages:packages_page',
]


admin.add_view(CategoryView(Category, db.session))
admin.add_view(PackageView(Package, db.session))
admin.add_view(PyPIView(PyPI, db.session))
admin.add_view(GithubView(Github, db.session))


def create_app(config):
    app = Flask('flask_toolbox/web')
    app.config.from_object(config)

    db.init_app(app)
    admin.init_app(app)

    for blueprint in blueprints:
        app.register_blueprint(import_string(blueprint))

    return app
