from marvin import db
from marvin.models import Stream, Movie
from marvin.tests import TestCaseWithTempDB

import ujson as json

class StreamDetailViewTest(TestCaseWithTempDB):

    def setUp(self):
        super(StreamDetailViewTest, self).setUp()
        movie = Movie(title='Titanic')
        stream = Stream(name='CinemaSins', movie=movie)
        with self.app.test_request_context():
            db.session.add(movie)
            db.session.add(stream)
            db.session.commit()
            self.stream_id = stream.id
            self.movie_id = movie.id


    def test_detail_view(self):
        response = self.client.get('/streams/%d' % self.stream_id)
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data)
        self.assertEqual(json_response['stream']['name'], 'CinemaSins')
        self.assertEqual(json_response['stream']['movie']['title'], 'Titanic')


    def test_delete(self):
        response = self.client.delete('/streams/%d' % self.stream_id)
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data)
        self.assertEqual(json_response['msg'], 'Stream deleted.')
        with self.app.test_request_context():
            self.assertEqual(len(Stream.query.all()), 0)


    def test_put(self):
        stream = {
            'id': self.stream_id,
            'name': 'Curiosa', # We change the name of the stream
        }
        response = self.client.put('/streams/%d' % self.stream_id, data=stream)
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data)
        self.assertEqual(json_response['msg'], 'Stream updated.')
        self.assertEqual(json_response['stream']['id'], self.stream_id)
        with self.app.test_request_context():
            new_stream = Stream.query.get(self.stream_id)
            self.assertEqual(new_stream.name, 'Curiosa')


    def test_invalid_put(self):
        stream = {
            'id': self.stream_id,
            'name': '',
        }
        response = self.client.put('/streams/%d' % self.stream_id, data=stream)
        self.assertEqual(response.status_code, 400)
        json_response = json.loads(response.data)
        self.assertEqual(json_response['msg'], 'Validation failed.')
        self.assertTrue('errors' in json_response)
