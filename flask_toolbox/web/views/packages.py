#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import Blueprint, render_template


packages_page = Blueprint('packages_page', __name__,
                          template_folder='templates')


@packages_page.route('/packages')
def index():
    return render_template('packages.html')
