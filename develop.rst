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

    (venv)$ python manage.py init_db
    (venv)$ python manage.py init_data

Run the server::

    (venv)$ python manage.py runserver

Run the crawler
---------------

start the redis server::

    $ redis-server

start the rabbitmq server::

    $ rabbitmq-server

set up a github token(in case that you may hit the github api rate limit)::

    $ export GITHUB_TOKEN="xxx"

start the celery worker::

    $ celery -A manage.celery_app worker --loglevel=info

start the crawler::

    $ python manage.py update_data
