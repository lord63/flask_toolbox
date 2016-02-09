#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import Blueprint, render_template


package_page = Blueprint('package_page', __name__,
                         template_folder='templates')


@package_page.route('/packages/<package>')
def index(package):
    return render_template('package.html')
