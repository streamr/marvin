from marvin.models import Movie
from marvin.tests import TestCaseWithTempDB

from mock import Mock, patch

class OMDBFetchTest(TestCaseWithTempDB):

    def setUp(self):
        # We can't import the tasks module until create_app has been called,
        # which is why we do it down here
        from marvin.tasks import external_search
        self.external_search = external_search


    def test_query_omdb(self):
        # Supply a mock of requests
        attrs = {
            'json.return_value': {
                u'Search': [
                    {
                        u'imdbID': u'tt0109179',
                        u'Year': u'1998',
                        u'Type': u'movie',
                        u'Title': u"Ava's Magical Adventure"
                    },
                    {
                        u'imdbID': u'tt0798009',
                        u'Year': u'2004',
                        u'Type': u'episode',
                        u'Title': u'Ava Gardner: Another Touch of Venus'
                    },
                    {
                        u'imdbID': u'tt1548011',
                        u'Year': u'2008',
                        u'Type': u'movie',
                        u'Title': u'Stalking Ava Gardner'
                    },
                    {
                        u'imdbID': u'tt0363371',
                        u'Year': u'1975',
                        u'Type': u'series',
                        u'Title': u'Signora Ava'
                    }
                ]
            },
            'status_code': 200,
        }
        response = Mock(**attrs)
        requests = Mock(**{'get.return_value': response})

        # pylint: disable=multiple-statements
        with patch('marvin.tasks.requests', requests), self.app.test_request_context():
            self.external_search('ava')
        with self.app.test_request_context():
            # we expect the 'series'-type to be ignored
            self.assertEqual(len(Movie.query.all()), 3)


    def test_no_duplicate_movies(self):
        movie = Movie(
            title='The Hobbit: The Desolation of Smaug',
            external_id='imdb:tt1170358',
        )
        self.addItems(movie)
        attrs = {
            'json.return_value': {
                "Search": [
                    {
                        "Title": "The Hobbit: An Unexpected Journey",
                        "Type": "movie",
                        "Year": "2012",
                        "imdbID": "tt0903624"
                    },
                    {
                        "Title": "The Hobbit: The Desolation of Smaug",
                        "Type": "movie",
                        "Year": "2013",
                        "imdbID": "tt1170358"
                    }
                ]
            },
            'status_code': 200,
        }
        response = Mock(**attrs)
        requests = Mock(**{'get.return_value': response})

        # pylint: disable=multiple-statements
        with patch('marvin.tasks.requests', requests), self.app.test_request_context():
            self.external_search('the hobbit')
            self.assertEqual(len(Movie.query.all()), 2)
