from flask_toolbox.crawler.crawler import Crawler


class DummyResponse(object):
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


def test_get_pypi_info_uses_pypistats(monkeypatch):
    requested_urls = []

    def fake_get(url):
        requested_urls.append(url)
        if url.endswith('/json'):
            return DummyResponse({
                'info': {
                    'version': '1.0.0',
                    'classifiers': [],
                },
                'urls': [{'upload_time': '2024-01-02T03:04:05'}],
                'releases': {
                    '1.0.0': [{'upload_time': '2024-01-02T03:04:05'}],
                },
            })
        if url == 'https://pypistats.org/api/packages/Flask-Testing/recent?period=month':
            return DummyResponse({
                'data': {
                    'last_month': 321,
                }
            })
        raise AssertionError('Unexpected URL: {0}'.format(url))

    monkeypatch.setattr('flask_toolbox.crawler.crawler.requests.get', fake_get)

    meta = Crawler().get_pypi_info('https://pypi.org/project/Flask-Testing/')

    assert requested_urls == [
        'https://pypi.org/project/Flask-Testing/json',
        'https://pypistats.org/api/packages/Flask-Testing/recent?period=month',
    ]
    assert meta.download_num == 321


def test_get_github_info_passes_repo_url_to_github_meta(monkeypatch):
    captured = {}

    def fail_get(url):
        raise AssertionError('Crawler should not fetch GitHub HTML: {0}'.format(url))

    class DummyGithubMeta(object):
        def __init__(self, url):
            captured['url'] = url

    monkeypatch.setattr('flask_toolbox.crawler.crawler.requests.get', fail_get)
    monkeypatch.setattr('flask_toolbox.crawler.crawler.GithubMeta', DummyGithubMeta)

    Crawler().get_github_info('https://github.com/pallets/flask')

    assert captured['url'] == 'https://github.com/pallets/flask'
