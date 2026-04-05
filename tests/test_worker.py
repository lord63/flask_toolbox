from flask_toolbox.crawler.worker import calculate_package_score
from flask_toolbox.extensions import db
from flask_toolbox.models import Package


def test_calculate_package_score_updates_non_flask_packages(app, sample_data):
    calculate_package_score()

    package = Package.query.filter_by(name="Flask-Testing").first()
    other_package = Package.query.filter_by(name="Pytest-Flask").first()

    assert package.score == 68.379
    assert other_package.score == 81.308
    assert Package.query.filter_by(name="Flask").first().score == 100.0


def test_calculate_package_score_caps_scores_at_100(app, sample_data):
    package = Package.query.filter_by(name="Pytest-Flask").first()
    package.github_info.watchers = 1000
    package.github_info.forks = 500
    package.pypi_info.download_num = 10_000
    db.session.commit()

    calculate_package_score()

    assert Package.query.filter_by(name="Pytest-Flask").first().score == 100.0
