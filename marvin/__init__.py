"""
    marvin
    ~~~~~~

    This is the main entry point to marvin, the API endpoints for streamr.
"""

# pylint: disable=invalid-name
from . import utils
from .security import before_request_authentication

from celery import Celery
from flask import Flask
from flask.ext.principal import Principal
from flask.ext.sqlalchemy import SQLAlchemy
from logging import getLogger
from sqlalchemy_defaults import make_lazy_configured
from os import path, environ

import logging.config
import sqlalchemy
import yaml


api = utils.ApiBase()
db = SQLAlchemy()
principal = Principal()

_logger = getLogger('marvin')


def create_app(config_file=None, **extra_config):
    """ Creates a WSGI app.

    :param config_file: Load config from this file.
    :param extra_config: Extra configuration values to pass to the WSGI object.
    """
    app = Flask(__name__)

    _configure_app(app, config_file, **extra_config)
    _configure_logging(app)
    _connect_extensions(app)

    # Configure lazy models
    make_lazy_configured(sqlalchemy.orm.mapper)

    _connect_blueprints(app)
    _connect_api_endpoints(app)
    _connect_utilities(app)

    # Import modules that connect to signals
    from . import permissions as _

    return app


def _configure_app(app, config_file=None, **extra_config):
    # Load the core settings
    core_settings = path.abspath(path.join(path.dirname(__file__), 'settings.py'))
    app.config.from_pyfile(core_settings)

    # Load from specified config file
    if config_file is not None:
        app.config.from_pyfile(config_file)

    # Load from environment specified config
    if 'MARVIN_CONFIG_FILE' in environ:
        print("Loading config from %s..." % environ['MARVIN_CONFIG_FILE'])
        app.config.from_envvar('MARVIN_CONFIG_FILE')

    # Override with any kwargs given
    app.config.update(extra_config)


def _configure_logging(app):
    """ Configures log handlers for the app, if necessary. Log config can be ignored if TESTING=True or DEBUG=True. """
    log_conf_path = app.config.get('LOG_CONF_PATH')
    if log_conf_path:
        print("Loading log config from %s" % log_conf_path)
        _init_logging(log_conf_path)
    else:
        ignore_absent_logging = app.config.get('DEBUG') or app.config.get('TESTING')
        if not ignore_absent_logging:
            raise ValueError('ERROR: LOG_CONF_PATH not found in config, terminating.')


def _connect_extensions(app):
    db.init_app(app)
    api.init_app(app)
    principal.init_app(app)


def _connect_blueprints(app):
    # Import views (must be done down here to avoid circular imports)
    from .views import stats
    from .views import promo

    app.register_blueprint(stats.mod)
    app.register_blueprint(promo.mod)


def _connect_api_endpoints(app):
    # Import views (must be done down here to avoid circular imports)
    from .views import movies
    from .views import streams
    from .views import entries
    from .views import users

    api.add_resource(movies.AllMoviesView, '/movies')
    api.add_resource(movies.MovieDetailView, '/movies/<int:movie_id>')
    api.add_resource(streams.CreateStreamView, '/movies/<int:movie_id>/createStream')
    api.add_resource(streams.StreamDetailView, '/streams/<int:stream_id>')
    api.add_resource(streams.StreamEntrySearch, '/streams/<int:stream_id>/entries')
    api.add_resource(entries.CreateEntryView, '/streams/<int:stream_id>/createEntry')
    api.add_resource(entries.EntryDetailView, '/entries/<int:entry_id>')
    api.add_resource(users.CreateUserView, '/users')
    api.add_resource(users.UserDetailView, '/users/<int:user_id>')
    api.add_resource(users.LoginView, '/login')


def _connect_utilities(app):
    # Error handler
    app.register_error_handler(500, utils.error_handler)

    # Connect before and after request handlers
    app.before_request(before_request_authentication)


def _init_logging(log_conf_path):
    """ Configure logging with the config given. """
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
