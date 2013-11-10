"""
    marvin.settings
    ~~~~~~~~~~~~~~~

    These are the core settings marvin needs to work properly.

    Some settings are not set here and need to be set in a local file, namely:

    * `SQLALCHEMY_DATABASE_URI`
    * `LOG_CONF_PATH`
    * `SECRET_KEY`
    * `CELERY_BROKER_URL`

    The path to this file can either be set by the envvar MARVIN_CONFIG_FILE or as a
    parameter to :func:`marvin.create_app`.
"""

SQLALCHEMY_COMMIT_ON_TEARDOWN = True

WTF_CSRF_ENABLED = False

# prevent flask from messing with log handlers
LOGGER_NAME = 'nonexistent'
