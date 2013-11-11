from marvin.models import Movie, Stream
from marvin.tests import TestCaseWithTempDB

from mock import Mock, patch

import ujson as json
import unittest

class AllMovieViewTest(TestCaseWithTempDB):

    def setUp(self):
        avatar = Movie(
            title='Avatar',
            external_id='imdb:tt0499549',
        )
        titanic = Movie(
            title='Titanic',
            external_id='imdb:tt0120338',
        )
        self.addItems(avatar, titanic)


    def test_search(self):
        with patch('marvin.tasks.external_search', Mock()):
            response = self.client.get('/movies?q=ava')
        json_response = self.assert200(response)
        self.assertEqual(len(json_response['movies']), 1)
        self.assertEqual(json_response['movies'][0]['title'], 'Avatar')


    def test_search_results_empty_fetches_external(self):
        # Search results for stuff we don't have should fetch more synchronously

        def create_movie(query): # pylint: disable=unused-argument
            movie = Movie(
                title='Harry Potter',
                external_id='imdb:tt0241527'
            )
            self.addItems(movie)

        external_search = Mock(side_effect=create_movie)
        with patch('marvin.tasks.external_search', external_search):
            response = self.client.get('/movies?q=harry')
        json_response = self.assert200(response)
        self.assertEqual(len(json_response['movies']), 1)


    @unittest.skip("Should be reactivated when we want to support POST creation of movies")
    def test_post_movie(self):
        movie = {
            'title': 'Avatar',
        }
        response = self.client.post('/movies', data=movie)
        self.assertEqual(response.headers['content-type'], 'application/json')
        self.assertValidCreate(response, object_name='movie')


    @unittest.skip("Should be reactivated when we want to support POST creation of movies")
    def test_add_invalid_movie(self):
        movie = {
            'title': '', # title field should be required
        }
        response = self.client.post('/movies', data=movie)
        self.assertValidClientError(response)


class MovieDetailView(TestCaseWithTempDB):

    def setUp(self):
        """ Add a single movie 'Red' to the db. """
        movie = Movie(
            title='Red',
            external_id='imdb:tt1245526',
        )
        (self.movie_id,) = self.addItems(movie)


    def test_details_view(self):
        response = self.client.get('/movies/%d' % self.movie_id)
        json_response = self.assert200(response)
        self.assertEqual(json_response['movie']['title'], 'Red')


    def test_details_contains_links(self):
        response = self.client.get('/movies/%d' % self.movie_id)
        json_response = self.assert200(response)
        print json_response
        self.assertTrue('createStream' in json_response['movie']['_links'])
        # links should be absolute
        self.assertTrue(json_response['movie']['_links']['createStream'].startswith('http'))
        self.assertTrue(json_response['movie']['_links']['createStream'].endswith('/movies/%d/createStream' %
            self.movie_id))


    def test_delete(self):
        response = self.client.delete('/movies/%d' % self.movie_id)
        json_response = self.assert200(response)
        self.assertEqual(json_response['msg'], 'Movie deleted.')
        with self.app.test_request_context():
            movies = Movie.query.all()
            self.assertEqual(len(movies), 0)
        with patch('marvin.tasks.external_search', Mock()):
            frontpage_json = json.loads(self.client.get('/movies').data)
        self.assertEqual(len(frontpage_json['movies']), 0)


    def test_get_nonexistent(self):
        response = self.client.get('/movies/65432')
        self.assert404(response)


    def test_delete_nonexistent(self):
        response = self.client.delete('/movies/543')
        self.assert404(response)


class MovieDetailWithStreams(TestCaseWithTempDB):

    def setUp(self):
        movie = Movie(
            title='Red',
            external_id='imdb:tt1245526'
        )
        sins_stream = Stream(name='CinemaSins', movie=movie)
        actors_stream = Stream(name="Who's that actor?", movie=movie)
        self.movie_id, self.sins_stream_id, self.actors_stream_id = self.addItems(movie, sins_stream, actors_stream)


    def test_stream_in_details(self):
        response = self.client.get('/movies/%d' % self.movie_id)
        json_response = self.assert200(response)
        self.assertTrue('streams' in json_response['movie'])
        self.assertTrue(len(json_response['movie']['streams']), 2)


class MovieLimitsInSearch(TestCaseWithTempDB):

    def setUp(self):
        for i in xrange(16):
            movie = Movie(
                title='Avatar %d' % i,
                external_id='imdb:tt02415 %d' % i,
            )
            self.addItems(movie)


    def test_movie_search_limits(self):
        with patch('marvin.tasks.external_search', Mock()):
            response = self.client.get('/movies?q=ava')
        json_response = self.assert200(response)
        self.assertEqual(len(json_response['movies']), 15)
