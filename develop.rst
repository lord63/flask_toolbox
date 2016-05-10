Development Guide
==================

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
