"""
    marvin.celery
    ~~~~~~~~~~~~~

    This is the entrypoint celery runs when listening for tasks from marvin.

"""
# pylint: disable=invalid-name,unused-import

from marvin import make_celery

celery = make_celery()

import marvin.tasks as _

if __name__ == '__main__':
    celery.start()
