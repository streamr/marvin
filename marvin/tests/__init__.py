# pylint: disable=attribute-defined-outside-init

from marvin import create_app, db

import os
import tempfile
import unittest

class MarvinBaseTestCase(unittest.TestCase):

    response_code_helpers = (
        200,
        201,
        400,
        404,
    )

    def __call__(self, result=None, **kwargs):
        """ Do setup here, so that we don't have to do super() calls in every subclass. """
        try:
            self._pre_setup()
            super(MarvinBaseTestCase, self).__call__(result)
        finally:
            self._post_teardown()


    def _pre_setup(self):
        """ Make sure to remove any envvars that might affect test runs. """
        for response_code in self.response_code_helpers:
            self.__dict__['assert%s' % response_code] = self._assert_status_factory(response_code)
        self._original_config_file_from_envvar = os.environ.get('MARVIN_CONFIG_FILE')
        if 'MARVIN_CONFIG_FILE' in os.environ:
            del os.environ['MARVIN_CONFIG_FILE']


    def _post_teardown(self):
        """ Restore any envvars we tampered with. """
        if self._original_config_file_from_envvar:
            os.environ['MARVIN_CONFIG_FILE'] = self._original_config_file_from_envvar


    def assert_status(self, response, status):
        self.assertEqual(response.status_code, status)


    def _assert_status_factory(self, code):
        def _assert_status(response):
            return self.assert_status(response, code)
        return _assert_status


class TestCaseWithTempDB(MarvinBaseTestCase):
    """ Inherit from this TestCase if you're doing anything that requires a test
    database. Remember to call super() if you override setUp and/or tearDown.
    """

    def _pre_setup(self):
        super(TestCaseWithTempDB, self)._pre_setup()
        self.tmp_config = tempfile.NamedTemporaryFile(delete=False)
        self.tmp_config.write('\n'.join([
            "SQLALCHEMY_DATABASE_URI = 'sqlite:///../tmptestdb.sqlite'",
            "CELERY_BROKER_URL = 'amqp://'",
            "TESTING = True",
            ]).encode('utf-8')
        )
        self.tmp_config.close()
        os.environ['MARVIN_CONFIG_FILE'] = self.tmp_config.name
        self.app = create_app()
        self.client = self.app.test_client()
        with self.app.test_request_context():
            db.create_all()


    def _post_teardown(self):
        os.remove(self.tmp_config.name)
        db.session.remove()
        os.remove('../tmptestdb.sqlite')
        super(TestCaseWithTempDB, self)._post_teardown()


    def addItems(self, *args):
        """ Adds all items passed to the database. """
        result_ids = []
        with self.app.test_request_context():
            for item in args:
                db.session.add(item)
            db.session.commit()
            for item in args:
                result_ids.append(item.id)
        return result_ids
