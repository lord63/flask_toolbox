Development Guide
==================

Run the server
--------------

Clone the fresh source code::

    $ git clone https://github.com/lord63/flask_toolbox.git

Install the dependencies, it's recommand to set up a virtual environment::

    $ virtualenv venv
    $ . venv/bin/activate
    (venv)$ pip install -r requirements/requirements.txt

Initialize the database::

    (venv)$ export FLASK_APP=manage.py
    (venv)$ flask init_db
    (venv)$ flask init_data

Run the server::

    (venv)$ flask run

Run the crawler
---------------

set up a github token(in case that you may hit the github api rate limit)::

    $ export GITHUB_TOKEN="xxx"

start the crawler::

    $ flask update_data
