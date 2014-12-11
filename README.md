[ ![Codeship Status for nm6061/tool-share](https://www.codeship.io/projects/bfce8790-1b7c-0132-5846-72a9f7efc67d/status)](https://www.codeship.io/projects/34940)

What is ToolShare?
==================

ToolShare is a community-oriented application that facilitates sharing tools between members of a community in a simple, easy-to-use way.

Developer Instructions
======================

1. Clone the repository `git clone git@github.com:nm6061/toolshare.git`
1. Install Python Virtual Environment `pip install virtualenv`
1. Create a virtual environment `virtualenv venv`
1. Activate the virtual environment `\venv\Scripts\active` on Windows and `source venv/bin/activate` on MAC/UNIX
1. Install the dependencies `pip install -r requirements.txt`
1. Create the SQLite database file `python manage.py syncdb`
1. Start the development server `python manage.py runserver`
1. Navigate to [http://localhost:8000/](http://localhost:8000/)

Note on Testing
===============

The application sends out emails to the users. Please use valid email addresses when testing the application. 

Initial Data
============

Bundled with the source is a database fixtures file, app/fixtures/initial_data.json, that contains initial data to populate the database with when created via the `syncdb` command. The passwords listed in the fixture file are hashed. The unhashed passwords of the test users are:


| Email Address            | Password |
| ------------------------ | -------- |
| john.smith@toolshare.com | john     |
| cameron@toolshare.com    | cameron  |
| rob.chase@toolshare.com  | rob      |
| tester@toolshare.com     | test     |

\* These email addresses are not valid and emails sent to these addresses will bounce. However, this will not cause the application to malfunction.