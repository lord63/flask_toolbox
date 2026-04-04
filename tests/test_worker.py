from flask_toolbox.crawler.worker import calculate_package_score
from flask_toolbox.models import Package


def test_calculate_package_score_updates_non_flask_packages(app, sample_data):
    calculate_package_score()

    package = Package.query.filter_by(name="Flask-Testing").first()
    other_package = Package.query.filter_by(name="Pytest-Flask").first()

    assert package.score == 32.5
    assert other_package.score == 47.5
    assert Package.query.filter_by(name="Flask").first().score == 100.0
