#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function

import os

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
import yaml

from flask_toolbox.crawler.celery import celery_app
from flask_toolbox.crawler.worker import (update_package_pypi_info,
                                          update_package_github_info)
from flask_toolbox.web.app import create_app
from flask_toolbox.web.configs import ProductionConfig, DevelopmentConfig
from flask_toolbox.web.extensions import db
from flask_toolbox.web.models import Category, Package


CONFIG = (ProductionConfig if os.environ.get('FLASK_APP_ENV') == 'production'
          else DevelopmentConfig)
app = create_app(CONFIG)
manager = Manager(app)
migrate = Migrate(app, db)


def _make_context():
    """Return context dict for a shell session so you can access
    app and db by default.
    """
    return {'app': app, 'db': db}


@manager.command
def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
    print('Init the database.')


@manager.command
def init_data():
    with open('packages.yml') as f:
        data = yaml.load(f)

    for category_name, category_info in data['categories'].items():
        new_category = Category(
            name=category_name,
            description=category_info['description']
        )
        db.session.add(new_category)
        db.session.commit()

        for package in category_info['packages']:
            package_info = data['packages'][package]
            new_package = Package(
                category_id=new_category.id,
                name=package,
                description=package_info['description'],
                pypi_url=package_info['pypi_url'],
                documentation_url=package_info['documentation_url'],
                source_code_url=package_info['source_code_url'],
                bug_tracker_url=package_info['bug_tracker_url'],
            )
            db.session.add(new_package)
            db.session.commit()


@manager.command
def update_data():
    print('Update PyPI info...')
    update_package_pypi_info.delay()
    print('Update Github info...')
    update_package_github_info.delay()
    print('Done.')


manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
