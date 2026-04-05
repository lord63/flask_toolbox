import datetime

import pytest

from flask_toolbox.app import create_app
from flask_toolbox.extensions import db
from flask_toolbox.models import Category, Github, Package, PyPI


class DummyResponse:
    """Fake requests.Response for testing HTTP clients."""

    def __init__(self, payload=None, links=None, status_code=200):
        self._payload = payload or []
        self.links = links or {}
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


class TestConfig(object):
    SECRET_KEY = "test"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_data(app):
    category = Category(name="Testing", description="Testing tools.")
    flask_package = Package(
        name="Flask",
        description="The baseline package.",
        score=100.0,
        pypi_url="https://pypi.org/project/Flask/",
        documentation_url="https://flask.palletsprojects.com/",
        source_code_url="https://github.com/pallets/flask",
        bug_tracker_url="https://github.com/pallets/flask/issues",
    )
    first_package = Package(
        category=category,
        name="Flask-Testing",
        description="Testing helpers for Flask.",
        score=0.0,
        pypi_url="https://pypi.org/project/Flask-Testing/",
        documentation_url="https://pythonhosted.org/Flask-Testing/",
        source_code_url="https://github.com/jarus/flask-testing",
        bug_tracker_url="https://github.com/jarus/flask-testing/issues",
    )
    second_package = Package(
        category=category,
        name="Pytest-Flask",
        description="Pytest support for Flask applications.",
        score=0.0,
        pypi_url="https://pypi.org/project/pytest-flask/",
        documentation_url="https://pytest-flask.readthedocs.io/",
        source_code_url="https://github.com/pytest-dev/pytest-flask",
        bug_tracker_url="https://github.com/pytest-dev/pytest-flask/issues",
    )
    db.session.add_all([category, flask_package, first_package, second_package])
    db.session.flush()

    entries = [
        (
            flask_package,
            dict(download_num=1000, release_num=10, current_version="3.0.0",
                 released_date=datetime.datetime(2024, 1, 2, 3, 4, 5),
                 first_release=datetime.datetime(2010, 4, 1, 0, 0, 0),
                 python_version="3.10 3.11"),
            dict(watchers=100, forks=50, development_activity="Very active",
                 last_commit=datetime.datetime(2024, 1, 2, 3, 4, 5),
                 first_commit=datetime.datetime(2010, 4, 1, 0, 0, 0),
                 contributors=25, issues=12, pull_requests=4),
        ),
        (
            first_package,
            dict(download_num=400, release_num=5, current_version="1.0.0",
                 released_date=datetime.datetime(2024, 2, 1, 0, 0, 0),
                 first_release=datetime.datetime(2015, 5, 1, 0, 0, 0),
                 python_version="3.10 3.11"),
            dict(watchers=50, forks=25, development_activity="Active",
                 last_commit=datetime.datetime(2024, 2, 2, 0, 0, 0),
                 first_commit=datetime.datetime(2015, 5, 1, 0, 0, 0),
                 contributors=10, issues=3, pull_requests=1),
        ),
        (
            second_package,
            dict(download_num=600, release_num=6, current_version="2.0.0",
                 released_date=datetime.datetime(2024, 3, 1, 0, 0, 0),
                 first_release=datetime.datetime(2016, 6, 1, 0, 0, 0),
                 python_version="3.10 3.11"),
            dict(watchers=70, forks=35, development_activity="Active",
                 last_commit=datetime.datetime(2024, 3, 2, 0, 0, 0),
                 first_commit=datetime.datetime(2016, 6, 1, 0, 0, 0),
                 contributors=12, issues=4, pull_requests=2),
        ),
    ]

    for package, pypi_kwargs, github_kwargs in entries:
        db.session.add(PyPI(package=package, **pypi_kwargs))
        db.session.add(Github(package=package, **github_kwargs))

    db.session.commit()
    return {
        "category": category,
        "flask": flask_package,
        "packages": [first_package, second_package],
    }
