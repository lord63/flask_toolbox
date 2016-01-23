#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os

from flask_script import Manager, Shell

from flask_toolbox.web.app import create_app
from flask_toolbox.web.configs import ProductionConfig, DevelopmentConfig
from flask_toolbox.web.extensions import db


CONFIG = (ProductionConfig if os.environ.get('FLASK_APP_ENV') == 'production'
          else DevelopmentConfig)
app = create_app(CONFIG)
manager = Manager(app)


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


manager.add_command('shell', Shell(make_context=_make_context))


if __name__ == '__main__':
    manager.run()
