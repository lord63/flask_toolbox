import requests
from urllib.parse import quote, urlparse

from flask_toolbox.crawler.pypi import PyPIMeta
from flask_toolbox.crawler.github import GithubMeta


class Crawler:
    def get_pypi_info(self, url):
        response = requests.get('{0}/json'.format(url.rstrip('/')))
        response.raise_for_status()
        package_name = urlparse(url).path.strip('/').split('/')[-1]
        try:
            download_response = requests.get(
                'https://pypistats.org/api/packages/{0}/recent?period=month'.format(
                    quote(package_name, safe='')
                )
            )
            download_response.raise_for_status()
            download_data = download_response.json()
        except requests.RequestException:
            download_data = {'data': {'last_month': 0}}
        package_info = PyPIMeta(response.json(), download_data)
        return package_info

    def get_github_info(self, url):
        repo_info = GithubMeta(url)
        return repo_info
