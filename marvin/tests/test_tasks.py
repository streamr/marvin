from marvin.models import Movie
from marvin.tests import TestCaseWithTempDB

from mock import Mock, patch

class OMDBFetchTest(TestCaseWithTempDB):

    def setUp(self):
        # We can't import the tasks module until create_app has been called,
        # which is why we do it down here
        from marvin import tasks
        self.parse_runtime_to_seconds = tasks.parse_runtime_to_seconds
        self.update_meta = tasks.update_meta_for_movie


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
        with patch('marvin.tasks.requests', requests):
            self.update_meta('imdb:tt1170358')
        with self.app.test_request_context():
            movie = Movie.query.get(movie_id)
            self.assertEqual(movie.duration_in_s, 161*60)
            self.assertEqual(movie.imdb_rating, 8.2)
            self.assertEqual(movie.number_of_imdb_votes, 206398)
            self.assertEqual(movie.metascore, 66)
            self.assertEqual(movie.cover_img,
                "http://ia.media-imdb.com/images/M/MV5BMjAxMjMzMzAxOV5BMl5BanBnXkFtZTcwNTU3NzU2OQ@@._V1_SX300.jpg")


    def test_parse_runtime(self):
        tests = [
            ('120 min', 7200),
            ('1 h 30 min', 5400),
            ('yeah, right', 0),
        ]
        for runtime, expected in tests:
            parsed = self.parse_runtime_to_seconds(runtime)
            self.assertEqual(parsed, expected)
