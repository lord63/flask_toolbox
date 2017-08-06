#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os

from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry


admin = Admin()
db = SQLAlchemy()
sentry = Sentry(dsn=os.environ.get('FLASK_TOOLBOX_SENTRY_DSN'))
