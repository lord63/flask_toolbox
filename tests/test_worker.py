from flask_toolbox.crawler.worker import (
    calculate_package_score,
    update_package_github_info,
    update_package_pypi_info,
)
from flask_toolbox.extensions import db
from flask_toolbox.models import Github, Package, PyPI


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


def test_update_package_pypi_info_keeps_existing_downloads_when_stats_are_unknown(
    app, sample_data, monkeypatch
):
    package = Package.query.filter_by(name="Flask-Testing").first()
    package.pypi_info.download_num = 400
    db.session.commit()

    class FakePackageInfo:
        download_num = None
        release_num = 5
        current_version = "1.0.1"
        released_date = package.pypi_info.released_date
        first_release = package.pypi_info.first_release
        python_version = package.pypi_info.python_version

    monkeypatch.setattr(
        "flask_toolbox.crawler.worker.Crawler.get_pypi_info",
        lambda self, url: FakePackageInfo(),
    )

    update_package_pypi_info(package.id)

    refreshed = PyPI.query.filter_by(package_id=package.id).first()
    assert refreshed.download_num == 400
    assert refreshed.current_version == "1.0.1"


def test_update_package_pypi_info_creates_null_downloads_for_first_sync(app, sample_data, monkeypatch):
    package = Package.query.filter_by(name="Pytest-Flask").first()
    released_date = package.pypi_info.released_date
    first_release = package.pypi_info.first_release
    python_version = package.pypi_info.python_version
    db.session.delete(package.pypi_info)
    db.session.commit()

    class FakePackageInfo:
        pass

    FakePackageInfo.download_num = None
    FakePackageInfo.release_num = 6
    FakePackageInfo.current_version = "2.0.1"
    FakePackageInfo.released_date = released_date
    FakePackageInfo.first_release = first_release
    FakePackageInfo.python_version = python_version

    monkeypatch.setattr(
        "flask_toolbox.crawler.worker.Crawler.get_pypi_info",
        lambda self, url: FakePackageInfo(),
    )

    update_package_pypi_info(package.id)

    created = PyPI.query.filter_by(package_id=package.id).first()
    assert created.download_num is None
    assert created.current_version == "2.0.1"


def test_update_package_github_info_updates_archived_flag(app, sample_data, monkeypatch):
    package = Package.query.filter_by(name="Flask-Testing").first()

    class FakeRepoInfo:
        watchers = 50
        forks = 25
        last_commit = package.github_info.last_commit
        contributors = 10
        issues = 3
        pull_requests = 1
        commits = 42
        archived = True

    monkeypatch.setattr(
        "flask_toolbox.crawler.worker.Crawler.get_github_info",
        lambda self, url: FakeRepoInfo(),
    )
    monkeypatch.setattr(
        "flask_toolbox.crawler.worker.get_development_activity",
        lambda url: "Inactive",
    )

    update_package_github_info(package.id)

    refreshed = Github.query.filter_by(package_id=package.id).first()
    assert refreshed.archived is True
