#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import Blueprint, render_template

from flask_toolbox.models import Category, Package


category_page = Blueprint('category_page', __name__,
                         template_folder='templates')


@category_page.route('/categories/<category>')
def index(category):
    the_category = Category.query.filter_by(name=category).first_or_404()
    related_packages = the_category.packages.order_by(Package.score.desc()).all()
    sidebar_title = "{0} packages in this category".format(len(related_packages))
    packages_list = [package.name for package in related_packages]
    return render_template(
        'category.html', category=the_category,
        related_packages=related_packages,
        sidebar_title=sidebar_title, packages_list=packages_list)
