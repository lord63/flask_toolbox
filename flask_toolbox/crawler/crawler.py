import time

import requests
from urllib.parse import quote, urlparse

from flask_toolbox.crawler.pypi import PyPIMeta
from flask_toolbox.crawler.github import GithubMeta


class Crawler:
    def get_pypi_info(self, url):
        response = requests.get('{0}/json'.format(url.rstrip('/')))
        response.raise_for_status()
        package_name = urlparse(url).path.strip('/').split('/')[-1]
        download_data = self._fetch_download_stats(package_name)
        package_info = PyPIMeta(response.json(), download_data)
        return package_info

    def _fetch_download_stats(self, package_name, retries=3, backoff=5):
        url = 'https://pypistats.org/api/packages/{0}/recent?period=month'.format(
            quote(package_name, safe='')
        )
        for attempt in range(retries):
            try:
                response = requests.get(url)
                if response.status_code == 429:
                    time.sleep(backoff * (attempt + 1))
                    continue
                response.raise_for_status()
                return response.json()
            except requests.RequestException:
                break
        return {'data': {'last_month': 0}}

    def get_github_info(self, url):
        repo_info = GithubMeta(url)
        return repo_info
