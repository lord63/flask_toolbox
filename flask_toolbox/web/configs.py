#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os


class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    ROOT = os.path.dirname(os.path.realpath(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(
        os.path.join(ROOT, 'flask_toolbox_dev.db'))


class ProductionConfig(Config):
    DEBUG = False


class TestConfig(Config):
    DEBUG = True
    TESTING = True
