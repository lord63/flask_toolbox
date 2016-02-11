#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import Blueprint, render_template

from flask_toolbox.web.models import Package


packages_page = Blueprint('packages_page', __name__,
                          template_folder='templates')


@packages_page.route('/packages')
def index():
    packages = Package.query.order_by(Package.name).all()
    sidebar_title = "All the packages"
    package_list = [package.name for package in packages]
    print(len(package_list))
    return render_template(
        'packages.html', packages=packages,
        sidebar_title=sidebar_title, package_list=package_list)
