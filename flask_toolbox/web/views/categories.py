#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import Blueprint, render_template

from flask_toolbox.web.models import Category


categories_page = Blueprint('categories_page', __name__,
                            template_folder='templates')


@categories_page.route('/categories')
def index():
    categories = Category.query.order_by(Category.name).all()
    sidebar_title = "All the categories"
    category_list = [category.name for category in categories]
    return render_template(
        'categories.html', categories=categories,
         sidebar_title=sidebar_title, category_list=category_list)
