from marvin.models import Movie

import unittest


class MovieTestCase(unittest.TestCase):

    def setUp(self):
        self.movie = Movie(
            year=1972,
            metascore=100,
            imdb_rating=9.2,
            number_of_imdb_votes=803353,
        )


    def test_update_relevancy(self):
        self.movie.update_relevancy()
        self.assertEqual(self.movie.relevancy, 202.59869915741038)
