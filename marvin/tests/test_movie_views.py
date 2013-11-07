from marvin import db
from marvin.models import Movie, Stream
from marvin.tests import TestCaseWithTempDB

import ujson as json

class AllMovieViewTest(TestCaseWithTempDB):

    def setUp(self):
        avatar = Movie(
            title='Avatar',
        )
        titanic = Movie(
            title='Titanic',
        )
        with self.app.test_request_context():
            db.session.add(avatar)
            db.session.add(titanic)
            db.session.commit()


    def test_search(self):
        response = self.client.get('/movies?q=ava')
        self.assert200(response)
        json_response = json.loads(response.data)
        self.assertEqual(len(json_response['movies']), 1)
        self.assertEqual(json_response['movies'][0]['title'], 'Avatar')


    def test_post_movie(self):
        movie = {
            'title': 'Avatar',
        }
        response = self.client.post('/movies', data=movie)
        self.assert201(response)
        self.assertEqual(response.headers['content-type'], 'application/json')
        json_response = json.loads(response.data)
        self.assertTrue('id' in json_response['movie'])
        movie_list = json.loads(self.client.get('/movies').data)
        self.assertEqual(len(movie_list['movies']), 1)
        self.assertTrue('Avatar' in movie_list['movies'][0].values())


    def test_add_invalid_movie(self):
        movie = {
            'title': '',
        }
        response = self.client.post('/movies', data=movie)
        self.assert400(response)
        json_response = json.loads(response.data)
        self.assertTrue('Data did not validate' in json_response['msg'])
        self.assertTrue('errors' in json_response)
        self.assertTrue('This field is required.' in json_response['errors']['title'])


class MovieDetailView(TestCaseWithTempDB):

    def setUp(self):
        """ Add a single movie 'Red' to the db. """
        movie = Movie(
            title='Red',
        )
        with self.app.test_request_context():
            db.session.add(movie)
            db.session.commit()
            self.movie_id = movie.id


    def test_details_view(self):
        response = self.client.get('/movies/%d' % self.movie_id)
        self.assert200(response)
        json_response = json.loads(response.data)
        self.assertEqual(json_response['movie']['title'], 'Red')


    def test_delete(self):
        response = self.client.delete('/movies/%d' % self.movie_id)
        self.assert200(response)
        json_response = json.loads(response.data)
        self.assertEqual(json_response['msg'], 'Movie deleted.')
        with self.app.test_request_context():
            movies = Movie.query.all()
            self.assertEqual(len(movies), 0)
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
        )
        sins_stream = Stream(name='CinemaSins', movie=movie)
        actors_stream = Stream(name="Who's that actor?", movie=movie)
        with self.app.test_request_context():
            db.session.add(movie)
            db.session.add(sins_stream)
            db.session.add(actors_stream)
            db.session.commit()
            self.movie_id = movie.id
            self.sins_stream_id = sins_stream.id
            self.actors_stream_id = actors_stream.id


    def test_stream_in_details(self):
        response = self.client.get('/movies/%d' % self.movie_id)
        json_response = json.loads(response.data)
        self.assertTrue('streams' in json_response['movie'])
        self.assertTrue(len(json_response['movie']['streams']), 2)
        self.assertTrue({
            'id': self.sins_stream_id,
            'name': 'CinemaSins'} in json_response['movie']['streams'])
        self.assertTrue({
            'id': self.actors_stream_id,
            'name': "Who's that actor?"} in json_response['movie']['streams'])
