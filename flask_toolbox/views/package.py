import math

from flask import Blueprint, render_template, url_for
from markupsafe import Markup

from flask_toolbox.models import Package


package_page = Blueprint('package_page', __name__,
                         template_folder='templates')


def _display_value(value):
    return value if value is not None and value != '' else 'unknown'


def _github_score_context(package, flask):
    package_watchers = package.github_info.watchers
    flask_watchers = flask.github_info.watchers
    package_forks = package.github_info.forks
    flask_forks = flask.github_info.forks
    if None in (package_watchers, flask_watchers, package_forks, flask_forks):
        return {
            'formula': 'unknown / unknown * 100 * 45% + unknown / unknown * 100 * 55%',
            'value': 'unavailable',
        }
    value = round(
        ((package_watchers / flask_watchers * 45 + package_forks / flask_forks * 55) / 2),
        3,
    )
    return {
        'formula': '{0} / {1} * 100 * 45% + {2} / {3} * 100 * 55%'.format(
            package_watchers, flask_watchers, package_forks, flask_forks
        ),
        'value': value,
    }


def _download_score_context(package, flask):
    package_downloads = package.pypi_info.download_num if package.pypi_info else None
    flask_downloads = flask.pypi_info.download_num if flask.pypi_info else None
    if package_downloads is None or flask_downloads is None:
        return {
            'formula': 'log(1 + unknown) / log(1 + unknown) * 100',
            'value': 'unavailable',
        }
    value = 0
    if flask_downloads > 0 and package_downloads > 0:
        value = round(
            min(math.log1p(package_downloads) / math.log1p(flask_downloads), 1) * 100, 3)
    return {
        'formula': 'log(1 + {0}) / log(1 + {1}) * 100'.format(
            package_downloads, flask_downloads
        ),
        'value': value,
    }


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
    github_score = _github_score_context(the_package, flask)
    download_score = _download_score_context(the_package, flask)
    return render_template(
        'score.html', package=the_package, flask=flask,
        display_value=_display_value,
        github_score=github_score,
        download_score=download_score,
        related_packages=related_packages, sidebar_title=sidebar_title)
