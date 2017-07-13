#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import Blueprint, render_template


home_and_intro = Blueprint('home_page', __name__,
                           template_folder='templates')


@home_and_intro.route('/')
def index():
    return render_template('home.html')


@home_and_intro.route('/intro')
def intr():
    return render_template('intro.html')
