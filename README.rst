Agenda de politicieni (contact list of politicians)
===================================================

http://agenda.grep.ro/

Installation
------------

1. Clone the Git repository::

    git clone git://github.com/alex-morega/agenda-politicieni.git
    cd agenda-politicieni

2. Create a Virtualenv_, activate it::

    virtualenv sandbox
    echo '*' > sandbox/.gitignore
    . sandbox/bin/activate

.. _Virtualenv: http://pypi.python.org/pypi/virtualenv

3. Install dependencies::

    pip install -r requirements-dev.txt

4. Create an `instance` folder and configuration file::

    mkdir instance
    echo "SECRET_KEY = 'some_random_stuff'" > instance/settings.py

5. Create the database structure using migrations::

    python migrations/manage.py version_control sqlite:///instance/agenda.db migrations
    python migrations/manage.py upgrade sqlite:///instance/agenda.db migrations

6. Import some data::

    curl 'http://agenda.grep.ro/download?format=json' > instance/datadump.json
    python agenda.py shell

    >>> import database
    >>> database.import_json('instance/datadump.json')

7. Run the development server::

    python agenda.py runserver
