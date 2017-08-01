#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import Flask
from werkzeug.utils import import_string

from flask_toolbox.extensions import db, admin
from flask_toolbox.models import Category, Package, PyPI, Github
from flask_toolbox.admin import (CategoryView, PackageView, PyPIView,
                                     GithubView)

blueprints = [
    'flask_toolbox.views.home:home_page',
    'flask_toolbox.views.category:category_page',
    'flask_toolbox.views.categories:categories_page',
    'flask_toolbox.views.package:package_page',
    'flask_toolbox.views.packages:packages_page',
]


admin.add_view(CategoryView(Category, db.session))
admin.add_view(PackageView(Package, db.session))
admin.add_view(PyPIView(PyPI, db.session))
admin.add_view(GithubView(Github, db.session))


def create_app(config):
    app = Flask('flask_toolbox')
    app.config.from_object(config)

    db.init_app(app)
    admin.init_app(app)

    for blueprint in blueprints:
        app.register_blueprint(import_string(blueprint))

    @app.context_processor
    def inject_statics():
        # FIXME: find a better way to exclude packages that don't have package_id.
        # Duplicated code in packages.py and home.py
        return dict(package_num=Package.query.filter(Package.category_id != None).count(),
                    category_num=Category.query.count())

    return app
