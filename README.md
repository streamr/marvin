marvin
======

[![Build Status](https://travis-ci.org/streamr/marvin.png?branch=master)](https://travis-ci.org/streamr/marvin)

API endpoints for streamr.

You can browse the [code coverage report] online!

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
[code coverage report]: http://streamr.github.io/marvin/coverage


To look at our webpage 
Make marvin knows which config file to run and that you have the python libraries:
    
    $ set MARVIN_CONFIG_FILE=..\dev_config.py
    $ venv\Scripts\activate.bat

Now you run the manage.py
    
    $ python manage.py runserver

Then open your browser and navigate to localhost:5000/promo
