""" Configuration used for the devserver. """

from os import path

SQLALCHEMY_DATABASE_URI = 'sqlite:///../db.sqlite'

SECRET_KEY = 'supersecret'

LOG_CONF_PATH = path.abspath(path.join(path.dirname(__file__), 'dev_log_conf.yaml'))


###########################################
############# Celery stuff
###########################################

CELERY_BROKER_URL = 'amqp://'
