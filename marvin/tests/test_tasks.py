from marvin.models import Movie
from marvin.tests import TestCaseWithTempDB

from mock import Mock, patch

class OMDBFetchTest(TestCaseWithTempDB):

    def setUp(self):
        # We can't import the tasks module until create_app has been called,
        # which is why we do it down here
        from marvin import tasks
        self.external_search = tasks.external_search
        self.find_cover_art = tasks.find_cover_art
        self.find_cover_art_for_movie = tasks.find_cover_art_for_movie
        self.find_duration_for_movie = tasks.find_duration_for_movie
        self.find_imdb_ratings_for_movie = tasks.find_imdb_ratings_for_movie
        self.find_metacritic_rating_for_movie = tasks.find_metacritic_rating_for_movie
        self.parse_runtime_to_seconds = tasks.parse_runtime_to_seconds


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
        patch_requests = patch('marvin.tasks.requests', requests)
        patch_cover_art = patch('marvin.tasks.find_cover_art', Mock())
        patch_durations = patch('marvin.tasks.find_durations', Mock())
        with patch_requests, patch_cover_art, self.app.test_request_context(), patch_durations:
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
        patch_requests = patch('marvin.tasks.requests', requests)
        patch_cover_art = patch('marvin.tasks.find_cover_art', Mock())
        patch_durations = patch('marvin.tasks.find_durations', Mock())
        with patch_requests, patch_cover_art, self.app.test_request_context(), patch_durations:
            self.external_search('the hobbit')
            self.assertEqual(len(Movie.query.all()), 2)


    def test_image_fetching(self):
        movie = Movie(
            title='The Hobbit: The Desolation of Smaug',
            external_id='imdb:tt1170358'
        )
        movie_id = self.addItems(movie)
        attrs = {
            'json.return_value': {
                "Actors": "Martin Freeman, Ian McKellen, Richard Armitage, Benedict Cumberbatch",
                "Director": "Peter Jackson",
                "Genre": "Adventure, Drama, Fantasy",
                "Plot": "The Dwarves, Bilbo and Gandalf have successfully escaped the Misty Mountains, and Bilbo " +
                    "has gained the One Ring. They all continue their journey to get their gold back from the " +
                    "Dragon, Smaug.",
                "Poster": "http://ia.media-imdb.com/images/M/MV5BMjAxMjMzMzAxOV5BMl5BanBnXkFtZTcwNTU3NzU2OQ@@._V1_" +
                    "SX300.jpg",
                "Rated": "N/A",
                "Released": "13 Dec 2013",
                "Response": "True",
                "Runtime": "N/A",
                "Title": "The Hobbit: The Desolation of Smaug",
                "Type": "N/A",
                "Writer": "Fran Walsh, Philippa Boyens",
                "Year": "2013",
                "imdbID": "tt1170358",
                "imdbRating": "N/A",
                "imdbVotes": "N/A"
            },
            'status_code': 200,
        }
        response = Mock(**attrs)
        requests = Mock(**{'get.return_value': response})
        artfinder = Mock()
        with patch('marvin.tasks.find_cover_art_for_movie', artfinder):
            self.find_cover_art()
        # Should have called the finder once
        self.assertEqual(len(artfinder.mock_calls), 1)
        with patch('marvin.tasks.requests', requests):
            self.find_cover_art_for_movie('imdb:tt1170358')
        with self.app.test_request_context():
            movie = Movie.query.get(movie_id)
            self.assertEqual(movie.cover_img,
                "http://ia.media-imdb.com/images/M/MV5BMjAxMjMzMzAxOV5BMl5BanBnXkFtZTcwNTU3NzU2OQ@@._V1_SX300.jpg")


    def test_add_with_missing_cover_art(self):
        movie = Movie(
            title='H&G',
            external_id='imdb:tt1170357',
        )
        movie_id = self.addItems(movie)
        attrs = {
            'json.return_value': {
                "Actors": "Ted Arcidi, Miryam Coppersmith, Arthur French, Patty Goodwin",
                "Director": u"Esther Dur\u00e1n, Caterina Klusemann",
                "Genre": "Short",
                "Plot": "N/A",
                "Poster": "N/A",
                "Rated": "N/A",
                "Released": "N/A",
                "Response": "True",
                "Runtime": "21 min",
                "Title": "H&G",
                "Type": "movie",
                "Writer": u"Caterina Klusemann, Esther Dur\u00e1n",
                "Year": "2000",
                "imdbID": "tt1170357",
                "imdbRating": "6.9",
                "imdbVotes": "12"
            },
            'status_code': 200,
        }
        response = Mock(**attrs)
        requests = Mock(**{'get.return_value': response})
        with patch('marvin.tasks.requests', requests):
            self.find_cover_art_for_movie('imdb:tt1170357')
        # Since Poster = N/A, should still be null
        with self.app.test_request_context():
            movie = Movie.query.get(movie_id)
            self.assertIsNone(movie.cover_img)


    def test_metadata_fetching(self):
        # Tests find_duration, find_metascore and find_imdb_ratings
        movie = Movie(
            title='The Hobbit: The Desolation of Smaug',
            external_id='imdb:tt1170358'
        )
        movie_id = self.addItems(movie)
        attrs = {
            'json.return_value': {
                "Actors": "Martin Freeman, Ian McKellen, Richard Armitage, Benedict Cumberbatch",
                "Director": "Peter Jackson",
                "Genre": "Adventure, Drama, Fantasy",
                "Plot": "The Dwarves, Bilbo and Gandalf have successfully escaped the Misty Mountains, and Bilbo " +
                    "has gained the One Ring. They all continue their journey to get their gold back from the " +
                    "Dragon, Smaug.",
                "Poster": "http://ia.media-imdb.com/images/M/MV5BMjAxMjMzMzAxOV5BMl5BanBnXkFtZTcwNTU3NzU2OQ@@._V1_" +
                    "SX300.jpg",
                "Rated": "N/A",
                "Released": "13 Dec 2013",
                "Metascore": "66",
                "Response": "True",
                "Runtime": "161 min",
                "Title": "The Hobbit: The Desolation of Smaug",
                "Type": "N/A",
                "Writer": "Fran Walsh, Philippa Boyens",
                "Year": "2013",
                "imdbID": "tt1170358",
                "imdbRating": "8.2",
                "imdbVotes": "206,398"
            },
            'status_code': 200,
        }
        response = Mock(**attrs)
        requests = Mock(**{'get.return_value': response})
        durationfinder = Mock()
        with patch('marvin.tasks.requests', requests):
            self.find_duration_for_movie('imdb:tt1170358')
            self.find_imdb_ratings_for_movie('imdb:tt1170358')
            self.find_metacritic_rating_for_movie('imdb:tt1170358')
        with self.app.test_request_context():
            movie = Movie.query.get(movie_id)
            self.assertEqual(movie.duration_in_s, 161*60)
            self.assertEqual(movie.imdb_rating, 8.2)
            self.assertEqual(movie.number_of_imdb_votes, 206398)
            self.assertEqual(movie.metascore, 66)


    def test_parse_runtime(self):
        tests = [
            ('120 min', 7200),
            ('1 h 30', 5400),
            ('yeah, right', 0),
        ]
        for runtime, expected in tests:
            parsed = self.parse_runtime_to_seconds(runtime)
            self.assertEqual(parsed, expected)
