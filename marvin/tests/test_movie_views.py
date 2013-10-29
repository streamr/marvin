from marvin import db
from marvin.models import Movie
from marvin.tests import TestCaseWithTempDB

import json

class AllMovieViewTest(TestCaseWithTempDB):

    def test_post_movie(self):
        movie = {
            'title': 'Avatar',
        }
        response = self.client.post('/movies', data=movie)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers['content-type'], 'application/json')

        movie_list = json.loads(self.client.get('/movies').data)
        self.assertEqual(len(movie_list['movies']), 1)
        self.assertTrue('Avatar' in movie_list['movies'][0].values())


    def test_add_invalid_movie(self):
        movie = {
            'title': '',
        }
        response = self.client.post('/movies', data=movie)
        self.assertEqual(response.status_code, 400)
        json_response = json.loads(response.data)
        self.assertTrue('Data did not validate' in json_response['msg'])
        self.assertTrue('errors' in json_response)
        self.assertTrue('This field is required.' in json_response['errors']['title'])


class MovieDetailView(TestCaseWithTempDB):

    def setUp(self):
        """ Add a single movie 'Red' to the db. """
        super(MovieDetailView, self).setUp()
        movie = Movie(title='Red')
        with self.app.test_request_context():
            db.session.add(movie)
            db.session.commit()
            self.movie_id = movie.id


    def test_details_view(self):
        response = self.client.get('/movies/%d' % self.movie_id)
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data)
        self.assertEqual(json_response['movie']['title'], 'Red')


    def test_delete(self):
        response = self.client.delete('/movies/%d' % self.movie_id)
        self.assertEqual(response.status_code, 204)
        with self.app.test_request_context():
            movies = Movie.query.all()
            self.assertEqual(len(movies), 0)
        frontpage_json = json.loads(self.client.get('/movies').data)
        self.assertEqual(len(frontpage_json['movies']), 0)

