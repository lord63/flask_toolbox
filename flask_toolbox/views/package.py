#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import Blueprint, render_template, Markup, url_for

from flask_toolbox.models import Package


package_page = Blueprint('package_page', __name__,
                         template_folder='templates')


@package_page.route('/packages')
def index():
    packages = Package.query.order_by(Package.name).filter(Package.category_id != None).all()
    sidebar_title = "All the packages"
    package_list = [package.name for package in packages]
    print(len(package_list))
    return render_template(
        'packages.html', packages=packages,
        sidebar_title=sidebar_title, package_list=package_list)


@package_page.route('/packages/<package>')
def show(package):
    the_package = Package.query.filter_by(name=package).first_or_404()
    category = the_package.category
    related_packages = [item.name for item in category.packages.order_by(Package.score.desc()).all()
                        if item.name != package]
    sidebar_title = (
        Markup("Other related packages in the <a href='{0}'>{1}</a> category".format(
             url_for('category_page.show', category=category.name),
             category.name
        ))
    )
    return render_template(
        'package.html', package=the_package,
        related_packages=related_packages, sidebar_title=sidebar_title)


@package_page.route('/packages/<package>/score')
def score(package):
    flask = Package.query.filter_by(name="Flask").first()
    the_package = Package.query.filter_by(name=package).first_or_404()
    category = the_package.category
    related_packages = [item.name for item in category.packages.order_by(Package.score.desc()).all()
                        if item.name != package]
    sidebar_title = (
        Markup("Other related packages in the <a href='{0}'>{1}</a> category".format(
             url_for('category_page.index', category=category.name),
             category.name
        ))
    )
    return render_template(
        'score.html', package=the_package, flask=flask,
        related_packages=related_packages, sidebar_title=sidebar_title)
