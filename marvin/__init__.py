"""
    marvin
    ~~~~~~

    This is the main entry point to marvin, the API endpoints for streamr.
"""

# pylint: disable=invalid-name

from flask import Flask, make_response
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api
from sqlalchemy_defaults import make_lazy_configured
from os import path, environ

import sqlalchemy
import ujson

db = SQLAlchemy()
api = Api()

@api.representation('application/json')
def _fastjson(data, code, headers=None):
    response = make_response(ujson.dumps(data), code)
    response.headers.extend(headers or {})
    return response

def create_app(config_file=None, **extra_config):
    """ Creates a WSGI app.

    :param config_file: Load config from this file.
    :param extra_config: Extra configuration values to pass to the WSGI object.
    """
    core_settings = path.abspath(path.join(path.dirname(__file__), 'settings.py'))

    # Setup app configuration
    app = Flask(__name__)
    app.config.from_pyfile(core_settings)
    if config_file is not None:
        app.config.from_pyfile(config_file)
    if 'MARVIN_CONFIG_FILE' in environ:
        app.config.from_envvar('MARVIN_CONFIG_FILE')
    app.config.update(extra_config)

    # Connect extensions
    db.init_app(app)
    api.init_app(app)

    # Configure lazy models
    make_lazy_configured(sqlalchemy.orm.mapper)

    # Import views (must be done down here to avoid circular imports)
    from .views import movies
    from .views import streams

    # Register resources
    api.add_resource(movies.AllMoviesView, '/movies')
    api.add_resource(movies.MovieView, '/movies/<int:movie_id>')
    api.add_resource(streams.StreamDetailView, '/streams/<int:stream_id>')

    return app


def init_db(app):
    """ Create the database with all tables for the given app. """
    with app.test_request_context():
        db.create_all()
