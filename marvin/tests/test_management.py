from marvin import create_app
from marvin.management import init_db
from marvin.tests import MarvinBaseTestCase

from mock import patch

import os

class ManagementCommandsTest(MarvinBaseTestCase):

    def test_init_db(self):
        app = create_app(SQLALCHEMY_DATABASE_URI='sqlite:///../nonexistent.db', DEBUG=True)
        with patch('marvin.management.app', app):
            init_db()
        self.assertTrue(os.path.exists('../nonexistent.db'))

    def tearDown(self):
        os.remove('../nonexistent.db')

