#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import Blueprint, render_template

from flask_toolbox.models import Category, Package


category_page = Blueprint('category_page', __name__,
                         template_folder='templates')


@category_page.route('/categories')
def index():
    categories = Category.query.order_by(Category.name).all()
    sidebar_title = "All the categories"
    category_list = [category.name for category in categories]
    return render_template(
        'categories.html', categories=categories,
         sidebar_title=sidebar_title, category_list=category_list)


@category_page.route('/categories/<category>')
def show(category):
    the_category = Category.query.filter_by(name=category).first_or_404()
    related_packages = the_category.packages.order_by(Package.score.desc()).all()
    sidebar_title = "{0} packages in this category".format(len(related_packages))
    packages_list = [package.name for package in related_packages]
    return render_template(
        'category.html', category=the_category,
        related_packages=related_packages,
        sidebar_title=sidebar_title, packages_list=packages_list)
