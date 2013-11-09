"""
    marvin
    ~~~~~~

    This is the main entry point to marvin, the API endpoints for streamr.
"""

# pylint: disable=invalid-name

from celery import Celery
from flask import Flask, make_response
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api
from sqlalchemy_defaults import make_lazy_configured
from os import path, environ

import logging.config
import sqlalchemy
import ujson
import yaml

db = SQLAlchemy()
api = Api()

@api.representation('application/json')
def _fastjson(data, code, headers=None):
    """ Replace the default json serializer with one based on ujson. """
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
        print("Loading config from %s..." % environ['MARVIN_CONFIG_FILE'])
        app.config.from_envvar('MARVIN_CONFIG_FILE')
    app.config.update(extra_config)

    # Init logging
    # We allow logging to be left unconfigured as long as DEBUG=True
    log_conf_path = app.config.get('LOG_CONF_PATH')
    if log_conf_path:
        init_logging(log_conf_path)
    else:
        ignore_absent_logging = app.config.get('DEBUG') or app.config.get('TESTING')
        if not ignore_absent_logging:
            print('ERROR: LOG_CONF_PATH not found in config, terminating.')
            return

    # Connect extensions
    db.init_app(app)
    api.init_app(app)

    # Configure lazy models
    make_lazy_configured(sqlalchemy.orm.mapper)

    # Import views (must be done down here to avoid circular imports)
    from .views import movies
    from .views import streams
    from .views import entries
    from .views import stats

    # Register blueprints
    app.register_blueprint(stats.mod)

    # Register resources
    api.add_resource(movies.AllMoviesView, '/movies')
    api.add_resource(movies.MovieView, '/movies/<int:movie_id>')
    api.add_resource(streams.AllStreamView, '/streams')
    api.add_resource(streams.StreamDetailView, '/streams/<int:stream_id>')
    api.add_resource(streams.StreamEntrySearch, '/streams/<int:stream_id>/entries')
    api.add_resource(entries.CreateEntryView, '/entries')
    api.add_resource(entries.EntryDetailView, '/entries/<int:entry_id>')

    return app


def init_db(app):
    """ Create the database with all tables for the given app. """
    with app.test_request_context():
        db.create_all()


def init_logging(log_conf_path):
    """ Initialize log config. """
    with open(log_conf_path) as log_conf_file:
        log_conf = yaml.load(log_conf_file)
    logging.config.dictConfig(log_conf)


def make_celery():
    """ Creates a celery object.

    Requires that create_app() can be called without arguments, so MARVIN_CONFIG_FILE should
    probably point to the config file you want to use.
    """
    app = create_app()
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        """ Wraps the base task to make sure it's run in an app context. """

        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
