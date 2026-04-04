import datetime

from flask_toolbox.crawler import github


class DummyResponse(object):
    def __init__(self, payload=None, links=None):
        self._payload = payload or []
        self.links = links or {}

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


def test_github_meta_properties(monkeypatch):
    def fake_api_request(url, params=None):
        if url.endswith("/repos/pallets/flask"):
            return DummyResponse({
                "watchers_count": 1234,
                "forks_count": 56,
                "open_issues_count": 17,
            })
        if url.endswith("/repos/pallets/flask/commits") and params == {"per_page": 1}:
            return DummyResponse(
                payload=[{
                    "commit": {
                        "committer": {
                            "date": "2024-01-02T03:04:05Z",
                        }
                    }
                }],
                links={"last": {"url": "https://api.github.com/repos/pallets/flask/commits?page=2345&per_page=1"}},
            )
        if url.endswith("/repos/pallets/flask/contributors"):
            return DummyResponse(
                payload=[{"id": 1}],
                links={"last": {"url": "https://api.github.com/repos/pallets/flask/contributors?page=67&per_page=1&anon=1"}},
            )
        if url.endswith("/repos/pallets/flask/pulls"):
            return DummyResponse(
                payload=[{"id": 1}],
                links={"last": {"url": "https://api.github.com/repos/pallets/flask/pulls?page=9&per_page=1&state=open"}},
            )
        raise AssertionError("Unexpected request: {0} {1}".format(url, params))

    monkeypatch.setattr(github, "api_request", fake_api_request)

    meta = github.GithubMeta("https://github.com/pallets/flask")

    assert meta.watchers == 1234
    assert meta.forks == 56
    assert meta.last_commit == datetime.datetime(2024, 1, 2, 3, 4, 5)
    assert meta.commits == 2345
    assert meta.contributors == 67
    assert meta.issues == 8
    assert meta.pull_requests == 9


def test_github_helpers(monkeypatch):
    recent_dates = [
        {"commit": {"committer": {"date": "2024-01-03T00:00:00Z"}}},
        {"commit": {"committer": {"date": "2024-01-02T00:00:00Z"}}},
        {"commit": {"committer": {"date": "2024-01-01T00:00:00Z"}}},
    ]

    def fake_api_request(url, params=None):
        if url.endswith("/repos/pallets/flask/commits") and params == {"page": 45, "per_page": 1}:
            return DummyResponse(payload=[{
                "commit": {
                    "committer": {
                        "date": "2010-04-01T00:00:00Z",
                    }
                }
            }])
        if url.endswith("/repos/pallets/flask/commits") and params == {"per_page": 100}:
            return DummyResponse(payload=recent_dates)
        raise AssertionError("Unexpected request: {0} {1}".format(url, params))

    monkeypatch.setattr(github, "api_request", fake_api_request)

    first_commit = github.get_first_commit("https://github.com/pallets/flask", 45)
    activity = github.get_development_activity("https://github.com/pallets/flask")

    assert first_commit == datetime.datetime(2010, 4, 1, 0, 0, 0)
    assert activity == "Inactive"
