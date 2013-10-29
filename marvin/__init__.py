"""
    marvin
    ~~~~~~

    This is the main entry point to marvin, the API endpoints for streamr.
"""

# pylint: disable=invalid-name

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api
from os import path

db = SQLAlchemy()
api = Api()

def create_app(config_file=None, **extra_config):
    """ Creates a WSGI app.

    :param config_file: Load config from this file.
    :param extra_config: Extra configuration values to pass to the WSGI object.
    """
    core_settings = path.join(path.dirname(__file__), 'settings.py')

    # Setup app configuration
    app = Flask(__name__)
    app.config.from_pyfile(core_settings)
    if config_file is not None:
        app.config.from_pyfile(config_file)
    app.config.update(extra_config)

    # Connect extensions
    db.init_app(app)
    api.init_app(app)

    # Import views (must be done down here to avoid circular imports)
    from .views import movies

    # Register resources
    api.add_resource(movies.MovieView, '/movies/<int:movie_id>')
    api.add_resource(movies.AllMoviesView, '/movies')

    return app


def init_db(app):
    """ Create the database with all tables for the given app. """
    with app.test_request_context():
        db.create_all()
