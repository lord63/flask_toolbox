import pytest


@pytest.mark.parametrize(
    ("method", "path", "status_code", "text"),
    [
        ("get", "/", 200, "Hopefully the missing toolbox for flask"),
        ("get", "/intro", 200, "Why choose flask toolbox?"),
        ("get", "/categories", 200, "All categories by name"),
        ("get", "/categories/Testing", 200, "Testing tools."),
        ("get", "/packages", 200, "All packages by name"),
        ("get", "/packages/Flask-Testing", 200, "Testing helpers for Flask."),
        ("get", "/packages/Flask-Testing/score", 200, "The popularity rating of"),
    ],
)
def test_view_routes_return_expected_responses(client, sample_data, method, path, status_code, text):
    response = getattr(client, method)(path)

    assert response.status_code == status_code
    assert text.encode("utf-8") in response.data


def test_search_route_redirects_when_keywords_are_blank(client, sample_data):
    response = client.post("/search", data={"keywords": "   "})

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_search_route_returns_matching_packages(client, sample_data):
    response = client.post("/search", data={"keywords": "Testing"})

    assert response.status_code == 200
    assert b"There is only 1 result for Testing" in response.data
    assert b"Flask-Testing" in response.data


def test_package_detail_shows_unknown_for_missing_metrics(client, sample_data):
    package = sample_data["packages"][0]
    package.pypi_info.download_num = None
    package.pypi_info.python_version = None
    package.github_info.development_activity = None
    package.github_info.first_commit = None
    from flask_toolbox.extensions import db
    db.session.commit()

    response = client.get("/packages/Flask-Testing")

    assert response.status_code == 200
    assert response.data.count(b"unknown") >= 4


def test_package_score_page_handles_unknown_metrics(client, sample_data):
    flask_package = sample_data["flask"]
    package = sample_data["packages"][0]
    flask_package.pypi_info.download_num = None
    package.pypi_info.download_num = None
    package.github_info.watchers = None
    package.github_info.forks = None
    from flask_toolbox.extensions import db
    db.session.commit()

    response = client.get("/packages/Flask-Testing/score")

    assert response.status_code == 200
    assert b"unknown" in response.data
    assert b"unavailable" in response.data
