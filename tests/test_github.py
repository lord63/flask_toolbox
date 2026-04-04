import datetime

from flask_toolbox.crawler import github


class DummyResponse(object):
    def __init__(self, text="", payload=None):
        self.text = text
        self._payload = payload or []

    def json(self):
        return self._payload


def test_github_meta_properties():
    response = DummyResponse("""
        <html>
          <a class="social-count">ignored</a>
          <a class="social-count">1,234</a>
          <a class="social-count">56</a>
          <relative-time datetime="2024-01-02T03:04:05Z"></relative-time>
          <span class="text-emphasized">2,345</span>
          <span class="text-emphasized">67</span>
          <span class="Counter">8</span>
          <span class="Counter">9</span>
        </html>
    """)
    meta = github.GithubMeta(response, "https://github.com/pallets/flask")

    assert meta.watchers == 1234
    assert meta.forks == 56
    assert meta.last_commit == datetime.datetime(2024, 1, 2, 3, 4, 5)
    assert meta.commits == 2345
    assert meta.contributors == 67
    assert meta.issues == 8
    assert meta.pull_requests == 9


def test_github_meta_contributors_falls_back_to_api(monkeypatch):
    response = DummyResponse("""
        <html>
          <a class="social-count">ignored</a>
          <a class="social-count">12</a>
          <a class="social-count">3</a>
          <relative-time datetime="2024-01-02T03:04:05Z"></relative-time>
          <span class="text-emphasized">45</span>
          <span class="text-emphasized"><span></span></span>
          <span class="Counter">1</span>
          <span class="Counter">2</span>
        </html>
    """)
    monkeypatch.setattr(
        github,
        "api_request",
        lambda url: DummyResponse(payload=[{"id": 1}, {"id": 2}, {"id": 3}]),
    )

    meta = github.GithubMeta(response, "https://github.com/pallets/flask")

    assert meta.contributors == 3
