from marvin import create_app, db

import os
import tempfile
import unittest

class MarvinBaseTestCase(unittest.TestCase):

    def setUp(self):
        """ Make sure to remove any envvars that might affect test runs. """
        self._original_config_file_from_envvar = os.environ.get('MARVIN_CONFIG_FILE')
        if 'MARVIN_CONFIG_FILE' in os.environ:
            del os.environ['MARVIN_CONFIG_FILE']

    def tearDown(self):
        """ Restore any envvars we tampered with. """
        if self._original_config_file_from_envvar:
            os.environ['MARVIN_CONFIG_FILE'] = self._original_config_file_from_envvar


class TestCaseWithTempDB(MarvinBaseTestCase):
    """ Inherit from this TestCase if you're doing anything that requires a test
    database. Remember to call super() if you override setUp and/or tearDown.
    """

    def setUp(self):
        super(TestCaseWithTempDB, self).setUp()
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.app = create_app(
            SQLALCHEMY_DATABASE_URI='sqlite:///%s' % os.path.relpath(self.temp_db.name))
        with self.app.test_request_context():
            db.create_all()
        self.temp_db.close()
        self.client = self.app.test_client()


    def tearDown(self):
        super(TestCaseWithTempDB, self).tearDown()
        db.session.remove()
        os.remove(self.temp_db.name)
