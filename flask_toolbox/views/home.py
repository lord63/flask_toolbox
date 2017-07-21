#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import Blueprint, render_template



home_page = Blueprint('home_page', __name__,
                           template_folder='templates')


@home_page.route('/')
def index():
    return render_template('home.html')


@home_page.route('/intro')
def intro():
    return render_template('intro.html')
