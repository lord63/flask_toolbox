#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import Flask

from flask_toolbox.web.extensions import db


def create_app(config):
    app = Flask('flask_toolbox')
    app.config.from_object(config)

    db.init_app(app)

    return app
