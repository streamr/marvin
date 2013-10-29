""" Use this module to start the python devserver.

You can either start it "manually" by running it in your shell::

    $ python run_devserver.py

Or (preferably), you wrap this with grunt::

    $ grunt server
"""
# pylint: disable=missing-docstring
from marvin import create_app, init_db

from os import path

def main():
    config_file = path.abspath('dev_config.py')
    app = create_app(config_file=config_file)
    init_db(app)
    app.run(debug=True)


if __name__ == '__main__':
    main()
