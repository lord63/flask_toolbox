#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function

import os

import click
from flask_migrate import Migrate, MigrateCommand
from flask.cli import FlaskGroup
from livereload import Server
import yaml

from flask_toolbox.crawler.worker import update_pypi_info, update_github_info
from flask_toolbox.app import create_app
from flask_toolbox.configs import ProductionConfig, DevelopmentConfig
from flask_toolbox.extensions import db
from flask_toolbox.models import Category, Package


CONFIG = (ProductionConfig if os.environ.get('FLASK_APP_ENV') == 'production'
          else DevelopmentConfig)
app = create_app(CONFIG)
app.app_context().push()
migrate = Migrate(app, db)


@app.cli.command()
def live():
    """"Set up a liveload server."""
    server = Server(app.wsgi_app)
    server.serve(port=5000)


@app.cli.command()
def init_db():
    """Initialize the database."""
    with app.app_context():
        db.drop_all()
        db.create_all()
    print('Init the database.')


@app.cli.command()
def init_data():
    """Seed the database with packages.yml"""
    with open('packages.yml') as f:
        data = yaml.load(f)

    flask_info = data['packages']['Flask']
    flask = Package(
        name='Flask',
        description=flask_info['description'],
        pypi_url=flask_info['pypi_url'],
        documentation_url=flask_info['documentation_url'],
        source_code_url=flask_info['source_code_url'],
        bug_tracker_url=flask_info['bug_tracker_url'],
    )
    db.session.add(flask)

    for category_name, category_info in data['categories'].items():
        new_category = Category(
            name=category_name,
            description=category_info['description']
        )
        db.session.add(new_category)

        for package_name in category_info['packages']:
            package_info = data['packages'][package_name]
            new_package = Package(
                category_id=new_category.id,
                name=package_name,
                description=package_info['description'],
                pypi_url=package_info['pypi_url'],
                documentation_url=package_info['documentation_url'],
                source_code_url=package_info['source_code_url'],
                bug_tracker_url=package_info['bug_tracker_url'],
            )
            db.session.add(new_package)
    db.session.commit()


@app.cli.command()
def sync_data():
    """Sync the database with packages.yml"""
    with open('packages.yml') as f:
        data = yaml.load(f)

    for category_name, category_info in data['categories'].items():
        category = Category.query.filter_by(name=category_name).first()
        if category:
            category.description = category_info['description']
        else:
            category = Category(
                name=category_name,
                description=category_info['description']
            )
        db.session.add(category)

        for package_name in category_info['packages']:
            package_info = data['packages'][package_name]
            package = Package.query.filter_by(name=package_name).first()
            if package:
                package_info.update({'name': package_name, 'category_id': category.id})
                db.session.query(Package).filter(Package.id==package.id).update(package_info)
            else:
                package = Package(
                    category_id=category.id,
                    name=package_name,
                    description=package_info['description'],
                    pypi_url=package_info['pypi_url'],
                    documentation_url=package_info['documentation_url'],
                    source_code_url=package_info['source_code_url'],
                    bug_tracker_url=package_info['bug_tracker_url'],
                )
            db.session.add(package)
    db.session.commit()


@app.cli.command()
def update_data():
    """Crawl package's github and PyPI info."""
    print('Update PyPI info...')
    update_pypi_info()
    print('Update Github info...')
    update_github_info()
    print('Done.')
