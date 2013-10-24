"""
    marvin
    ~~~~~~

    This is the main entry point to marvin, the API endpoints for streamr.
"""

from flask import Flask

from os import path

def create_app(config_file=None, **extra_config):
    """ Creates a WSGI app.

    :param config_file: Load config from this file.
    :param extra_config: Extra configuration values to pass to the WSGI object.
    """
    if config_file is None:
        config_file = path.join(path.dirname(__file__), '..', 'dev_config.py')

    app = Flask(__name__)
    app.config.from_pyfile(config_file)
    app.config.update(extra_config)
    return app
