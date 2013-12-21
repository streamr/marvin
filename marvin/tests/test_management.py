from marvin import create_app
from marvin.management import init_db, delete_streams_and_entries
from marvin.models import Movie, Stream, Entry
from marvin.tests import MarvinBaseTestCase, TestCaseWithTempDB, fixtures

from mock import patch

import os

class ManagementInitDbTest(MarvinBaseTestCase):

    def test_init_db(self):
        app = create_app(SQLALCHEMY_DATABASE_URI='sqlite:///../nonexistent.db', DEBUG=True)
        with patch('marvin.management.app', app):
            init_db()
        self.assertTrue(os.path.exists('../nonexistent.db'))


    def tearDown(self):
        os.remove('../nonexistent.db')


class ManagementWipeTest(TestCaseWithTempDB):

    def setUp(self):
        fixtures.load(self.app, fixtures.COMPLETE)


    def test_wipe(self):
        with patch('marvin.management.app', self.app), self.app.test_request_context():
            delete_streams_and_entries()

        with self.app.app_context():
            self.assertTrue(len(Movie.query.all()) > 0)
            self.assertEqual(Movie.query.first().number_of_streams, 0)
            self.assertEqual(len(Entry.query.all()), 0)
            self.assertEqual(len(Stream.query.all()), 0)


    def test_wipe_also_movies(self):
        with patch('marvin.management.app', self.app), self.app.test_request_context():
            delete_streams_and_entries(wipe_movies=True)

        with self.app.test_request_context():
            self.assertEqual(len(Movie.query.all()), 0)
            self.assertEqual(len(Entry.query.all()), 0)
            self.assertEqual(len(Stream.query.all()), 0)

