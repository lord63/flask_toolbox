Development Guide
==================

Run the server
--------------

Clone the fresh source code::

    $ git clone https://github.com/lord63/flask_toolbox.git

Install the dependencies with uv::

    $ uv sync

Initialize the database::

    $ export FLASK_APP=manage.py
    $ uv run flask init_db
    $ uv run flask init_data

Audit package metadata before syncing it into the database::

    $ uv run python -m flask_toolbox.package_audit packages.yml
    $ uv run flask check_packages

Run the server::

    $ uv run flask run

Run the crawler
---------------

set up a github token(in case that you may hit the github api rate limit)::

    $ export GITHUB_TOKEN="xxx"

start the crawler::

    $ uv run flask update_data
