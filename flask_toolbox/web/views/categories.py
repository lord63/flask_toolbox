#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import Blueprint, render_template


categories_page = Blueprint('categories_page', __name__,
                            template_folder='templates')


@categories_page.route('/categories')
def index():
    return render_template('categories.html')
