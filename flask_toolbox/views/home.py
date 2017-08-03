#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import or_

from flask_toolbox.models import Package


home_page = Blueprint('home_page', __name__,
                           template_folder='templates')


@home_page.route('/')
def index():
    return render_template('home.html')


@home_page.route('/intro')
def intro():
    return render_template('intro.html')


@home_page.route('/search', methods=['POST'])
def search():
    keywords = list(filter(lambda x: len(x) > 0, request.form['keywords'].split(' ')))
    if not len(keywords):
        return redirect(url_for('home_page.index'))
    name_query = [Package.name.ilike('%{0}%'.format(word)) for word in keywords]
    description_query = [Package.description.ilike('%{0}%'.format(word)) for word in keywords]
    query = name_query + description_query
    packages = Package.query.filter(Package.category_id != None).filter(or_(*query)).all()
    return render_template('search.html', packages=packages, keywords=request.form['keywords'] )
