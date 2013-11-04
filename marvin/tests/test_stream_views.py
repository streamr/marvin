from marvin import db
from marvin.models import Stream, Movie, Entry
from marvin.tests import TestCaseWithTempDB

import ujson as json

class StreamDetailViewTest(TestCaseWithTempDB):

    def setUp(self):
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
        self.assert200(response)
        json_response = json.loads(response.data)
        self.assertEqual(json_response['stream']['name'], 'CinemaSins')
        self.assertEqual(json_response['stream']['movie']['title'], 'Titanic')


    def test_delete(self):
        response = self.client.delete('/streams/%d' % self.stream_id)
        self.assert200(response)
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
        self.assert200(response)
        json_response = json.loads(response.data)
        self.assertEqual(json_response['msg'], 'Stream updated.')
        self.assertEqual(json_response['stream']['id'], self.stream_id)
        with self.app.test_request_context():
            new_stream = Stream.query.get(self.stream_id)
            self.assertEqual(new_stream.name, 'Curiosa')


    def test_get_nonexistent(self):
        response = self.client.get('/streams/7654')
        self.assert404(response)


    def test_delete_nonexistent(self):
        response = self.client.delete('/streams/654')
        self.assert404(response)


    def test_put_nonexistent(self):
        stream = {
            'name': "Who's that?",
        }
        response = self.client.put('/streams/6543', data=stream)
        self.assert404(response)


    def test_invalid_put(self):
        stream = {
            'id': self.stream_id,
            'name': '',
        }
        response = self.client.put('/streams/%d' % self.stream_id, data=stream)
        self.assert400(response)
        json_response = json.loads(response.data)
        self.assertEqual(json_response['msg'], 'Validation failed.')
        self.assertTrue('errors' in json_response)


    def test_create_stream(self):
        stream = {
            'movie_id': self.movie_id,
            'name': 'FactChecker',
        }
        response = self.client.post('/streams', data=stream)
        self.assert201(response)
        with self.app.test_request_context():
            streams = Stream.query.all()
            self.assertEqual(len(streams), 2)


    def test_create_invalid(self):
        stream = {
            # missing movie_id
            'name': 'FactChecker',
        }
        response = self.client.post('/streams', data=stream)
        self.assert400(response)
        json_response = json.loads(response.data)
        self.assertTrue('errors' in json_response)


class StreamEntryFetchTest(TestCaseWithTempDB):

    def setUp(self):
        with self.app.test_request_context():
            movie = Movie(title='Avatar')
            stream = Stream(name='DurationNotifier', movie=movie)
            db.session.add(movie)
            db.session.add(stream)
            for i in range(20):
                entry = Entry(entry_point_in_ms=i*60*1000,
                    content="We're now at %d minutes into the movie." % i, stream=stream)
                db.session.add(entry)
            db.session.commit()
            self.stream_id = stream.id


    def test_get_all_entries_for_stream(self):
        response = self.client.get('/streams/%d/entries' % self.stream_id)
        self.assert200(response)
        json_response = json.loads(response.data)
        self.assertEqual(len(json_response['entries']), 20)

        # should be returned in order of appearance
        previous_entrypoint = -1
        for entry in json_response['entries']:
            self.assertTrue(entry['entry_point_in_ms'] > previous_entrypoint)
            previous_entrypoint = entry['entry_point_in_ms']


    def test_get_limited_amount_of_entries(self):
        response = self.client.get('/streams/%d/entries?limit=5' % self.stream_id)
        self.assert200(response)
        json_response = json.loads(response.data)
        self.assertEqual(len(json_response['entries']), 5)

        # get 5 next ones
        last_starttime = json_response['entries'][-1]['entry_point_in_ms']
        response = self.client.get('/streams/%d/entries?limit=5&starttime_gt=%d' % (self.stream_id, last_starttime))
        self.assert200(response)
        json_response = json.loads(response.data)
        # Should respect both params
        self.assertEqual(len(json_response['entries']), 5)
        self.assertTrue(json_response['entries'][0], last_starttime + 60*1000)


    def test_get_entries_for_nonexistent_stream(self):
        response = self.client.get('/streams/76543/entries')
        self.assert404(response)