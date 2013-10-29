from marvin import create_app, db

import os
import tempfile
import unittest

class TestCaseWithTempDB(unittest.TestCase):
    """ Inherit from this TestCase if you're doing anything that requires a test
    database. Remember to call super() if you override setUp and/or tearDown.
    """

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.app = create_app(
            SQLALCHEMY_DATABASE_URI='sqlite:///%s' % os.path.relpath(self.temp_db.name))
        with self.app.test_request_context():
            db.create_all()
        self.temp_db.close()
        self.client = self.app.test_client()


    def tearDown(self):
        os.remove(self.temp_db.name)
