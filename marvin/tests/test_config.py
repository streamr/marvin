from os import path

SQLALCHEMY_DATABASE_URI = 'sqlite:///../testdb.sqlite'

CELERY_BROKER_URL = 'amqp://'

TESTING = True

SECRET_KEY = 'supersecret'

LOG_CONF_PATH = path.abspath(path.join(path.dirname(__file__), 'test_log_conf.yaml'))
