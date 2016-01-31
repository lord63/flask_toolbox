#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask_admin.contrib.sqla import ModelView


class CategoryView(ModelView):
    column_searchable_list = ['name']


class PackageView(ModelView):
    column_searchable_list = ['name']


class PyPIView(ModelView):
    column_searchable_list = ['package.name']


class GithubView(ModelView):
    column_searchable_list = ['package.name']
