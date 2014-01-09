#!/bin/sh

# Configure git
git remote set-url origin $REPO.git
git config --global user.email "tarjei@roms.no"
git config --global user.name "Tarjei Husøy (via Travis CI)"

# Set up test db
psql -U postgres -c "CREATE DATABASE marvin_test;"

# Create test settings
echo 'from os import path

SQLALCHEMY_DATABASE_URI = "postgresql://postgres@localhost:5432/marvin_test"

CELERY_BROKER_URL = "amqp://"

TESTING = True

SECRET_KEY = "supersecret"

LOG_CONF_PATH = path.abspath(path.join(path.dirname(__file__), "marvin", "tests", "test_log_conf.yaml"))
' > /tmp/testconfig.py

export MARVIN_TEST_CONFIG=/tmp/testconfig.py
