from marvin.models import Stream, Movie, Entry
from marvin.tests import TestCaseWithTempDB

class StreamDetailViewTest(TestCaseWithTempDB):

    def setUp(self):
        movie = Movie(
            title='Titanic',
            external_id='imdb:tt1245526',
        )
        stream = Stream(name='CinemaSins', movie=movie)
        self.stream_id, self.movie_id = self.addItems(stream, movie)


    def test_detail_view(self):
        response = self.client.get('/streams/%d' % self.stream_id)
        json_response = self.assert200(response)
        self.assertEqual(json_response['stream']['name'], 'CinemaSins')
        self.assertEqual(json_response['stream']['movie']['title'], 'Titanic')


    def test_delete(self):
        response = self.client.delete('/streams/%d' % self.stream_id)
        json_response = self.assert200(response)
        self.assertEqual(json_response['msg'], 'Stream deleted.')
        with self.app.test_request_context():
            self.assertEqual(len(Stream.query.all()), 0)


    def test_put(self):
        stream = {
            'id': self.stream_id,
            'name': 'Curiosa', # We change the name of the stream
        }
        response = self.client.put('/streams/%d' % self.stream_id, data=stream)
        json_response = self.assert200(response)
        self.assertEqual(json_response['msg'], 'Stream updated.')
        self.assertTrue(json_response['stream']['href'].endswith(str(self.stream_id)))
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
        self.assertValidClientError(response)


    def test_create_stream(self):
        stream = {
            'movie_id': self.movie_id,
            'name': 'FactChecker',
        }
        response = self.client.post('/streams', data=stream)
        self.assertValidCreate(response, object_name='stream')
        with self.app.test_request_context():
            streams = Stream.query.all()
            self.assertEqual(len(streams), 2)


    def test_create_invalid(self):
        stream = {
            # missing movie_id
            'name': 'FactChecker',
        }
        response = self.client.post('/streams', data=stream)
        self.assertValidClientError(response)


class StreamEntryFetchTest(TestCaseWithTempDB):

    def setUp(self):
        movie = Movie(
            title='Avatar',
            external_id='imdb:tt0499549',
        )
        stream = Stream(name='DurationNotifier', movie=movie)
        self.stream_id, _ = self.addItems(stream, movie)
        for i in range(20):
            entry = Entry(entry_point_in_ms=i*60*1000, title='<h1>Title</h1>',
                content="We're now at %d minutes into the movie." % i, stream=stream)
            self.addItems(entry)


    def test_get_all_entries_for_stream(self):
        response = self.client.get('/streams/%d/entries' % self.stream_id)
        json_response = self.assert200(response)
        self.assertEqual(len(json_response['entries']), 20)

        # should be returned in order of appearance
        previous_entrypoint = -1
        for entry in json_response['entries']:
            self.assertTrue(entry['entry_point_in_ms'] > previous_entrypoint)
            previous_entrypoint = entry['entry_point_in_ms']


    def test_get_limited_amount_of_entries(self):
        response = self.client.get('/streams/%d/entries?limit=5' % self.stream_id)
        json_response = self.assert200(response)
        self.assertEqual(len(json_response['entries']), 5)

        # get 5 next ones
        last_starttime = json_response['entries'][-1]['entry_point_in_ms']
        response = self.client.get('/streams/%d/entries?limit=5&starttime_gt=%d' % (self.stream_id, last_starttime))
        json_response = self.assert200(response)

        # Should respect both params
        self.assertEqual(len(json_response['entries']), 5)
        self.assertTrue(json_response['entries'][0], last_starttime + 60*1000)


    def test_get_entries_for_nonexistent_stream(self):
        response = self.client.get('/streams/76543/entries')
        self.assert404(response)
