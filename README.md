marvin
======

API endpoints for streamr.

Local development
-----------------

Make sure you have the python [virtualenv] tool installed, to create isolated python environments.

Create a virtualenv with the python dependencies:

    $ virtualenv venv
    $ pip install -r requirements.txt

If you don't have [node] installed yet, do that. Then, install grunt and our packages:

    $ npm install -g grunt-cli
    $ npm install

You can now start the devserver and get hacking:

    $ grunt server

[virtualenv]: https://pypi.python.org/pypi/virtualenv
[node]: http://nodejs.org/
