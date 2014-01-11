from marvin import create_app
from marvin.models import Movie, Stream, Entry
from marvin.tests import MarvinBaseTestCase, TestCaseWithTempDB, fixtures

from mock import patch

import os
import tempfile

class ManagementInitDbTest(MarvinBaseTestCase):

    def setUp(self):
        self.config_file = tempfile.NamedTemporaryFile(delete=False)
        self.config_file.write('\n'.join([
            'TESTING = True',
            "SQLALCHEMY_DATABASE_URI = 'sqlite:///../nonexistent.db'",
        ]).encode('utf-8'))
        self.config_file.close()
        os.environ['MARVIN_CONFIG_FILE'] = self.config_file.name


    def test_init_db(self):
        # must wait with import until setUp has been called
        from marvin.management import init_db

        app = create_app()
        with patch('marvin.management.app', app):
            init_db()
        self.assertTrue(os.path.exists('../nonexistent.db'))


    def tearDown(self):
        os.remove('../nonexistent.db')
#        del os.environ['MARVIN_CONFIG_FILE']


class ManagementWipeTest(TestCaseWithTempDB):

    def setUp(self):
        self.config_file = tempfile.NamedTemporaryFile(delete=False)
        self.config_file.write('\n'.join([
            'TESTING = True',
#            'CELERY_BROKER_URL = "amqp://"',
        ]).encode('utf-8'))
        self.config_file.close()
        os.environ['MARVIN_CONFIG_FILE'] = self.config_file.name

        from marvin.management import delete_streams_and_entries
        self.delete_streams_and_entries = delete_streams_and_entries
        fixtures.load(self.app, fixtures.COMPLETE)


    def tearDown(self):
        del os.environ['MARVIN_CONFIG_FILE']


    def test_wipe(self):
        with patch('marvin.management.app', self.app), self.app.test_request_context():
            self.delete_streams_and_entries()

        with self.app.app_context():
            self.assertTrue(len(Movie.query.all()) > 0)
            self.assertEqual(Movie.query.first().number_of_streams, 0)
            self.assertEqual(len(Entry.query.all()), 0)
            self.assertEqual(len(Stream.query.all()), 0)


    def test_wipe_also_movies(self):
        with patch('marvin.management.app', self.app), self.app.test_request_context():
            self.delete_streams_and_entries(wipe_movies=True)

        with self.app.test_request_context():
            self.assertEqual(len(Movie.query.all()), 0)
            self.assertEqual(len(Entry.query.all()), 0)
            self.assertEqual(len(Stream.query.all()), 0)
