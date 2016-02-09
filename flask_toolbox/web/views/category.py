#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import Blueprint, render_template


category_page = Blueprint('category_page', __name__,
                         template_folder='templates')


@category_page.route('/categories/<category>')
def index(category):
    return render_template('category.html')
