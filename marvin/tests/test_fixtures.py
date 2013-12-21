from marvin.models import Movie, Stream
from marvin.tests import TestCaseWithTempDB, fixtures

class FixtureTest(TestCaseWithTempDB):

    def test_load_fixture(self):
        fixtures.load(self.app, fixtures.COMPLETE)
        with self.app.test_request_context():
            self.assertTrue(len(Movie.query.all()) > 0)
            self.assertTrue(len(Stream.query.all()) > 0)
