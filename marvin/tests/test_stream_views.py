from marvin.models import Stream, Movie, Entry, User
from marvin.tests import TestCaseWithTempDB, AuthenticatedUserMixin

class StreamDetailViewTest(TestCaseWithTempDB, AuthenticatedUserMixin):

    def setUp(self):
        self.authenticate()
        movie = Movie(
            title='Titanic',
            external_id='imdb:tt1245526',
            number_of_streams=1,
        )

        stream = Stream(name='CinemaSins', movie=movie, creator=self.user, public=True)
        private_stream = Stream(name='Uncompleted', movie=movie, creator=self.user)
        self.stream_id, self.movie_id, self.p_str_id = self.addItems(stream, movie, private_stream)


    def test_detail_view(self):
        response = self.client.get('/streams/%d' % self.stream_id)
        json_response = self.assert200(response)
        self.assertEqual(json_response['stream']['name'], 'CinemaSins')
        self.assertEqual(json_response['stream']['movie']['title'], 'Titanic')
        self.assertEqual(json_response['stream']['author']['username'], 'bob')


    def test_delete(self):
        response = self.client.delete('/streams/%d' % self.stream_id, headers=self.auth_header)
        json_response = self.assert200(response)
        self.assertEqual(json_response['msg'], 'Stream deleted.')
        with self.app.test_request_context():
            self.assertEqual(len(Stream.query.all()), 1)
            movie = Movie.query.get(self.movie_id)
            self.assertEqual(movie.number_of_streams, 0)


    def test_delete_restricted(self):
        response = self.client.delete('/streams/%d' % self.stream_id)
        self.assert401(response)


    def test_delete_other_users_stream(self):
        with self.app.app_context():
            alice = User(username='alice', email='alice@example.com', password='alicepw')
            alice_id = self.addItems(alice)[0]
        stream = Stream(name='Alices stream', creator_id=alice_id, movie_id=self.movie_id)
        (stream_id,) = self.addItems(stream) # pylint: disable=unbalanced-tuple-unpacking
        response = self.client.delete('/streams/%d' % stream_id, headers=self.auth_header)
        self.assert403(response)


    def test_put(self):
        stream = {
            'id': self.stream_id,
            'name': 'Curiosa', # We change the name of the stream
        }
        response = self.client.put('/streams/%d' % self.stream_id, data=stream, headers=self.auth_header)
        json_response = self.assert200(response)
        self.assertEqual(json_response['stream']['name'], 'Curiosa')
        with self.app.test_request_context():
            new_stream = Stream.query.get(self.stream_id)
            self.assertEqual(new_stream.name, 'Curiosa')


    def test_put_restricted(self):
        stream = {
            'id': self.stream_id,
            'name': 'Curiosa', # We change the name of the stream
        }
        response = self.client.put('/streams/%d' % self.stream_id, data=stream)
        self.assert401(response)


    def test_edit_other_users_stream(self):
        with self.app.app_context():
            alice = User(username='alice', email='alice@example.com', password='alicepw')
            alice_id = self.addItems(alice)[0]
        stream = Stream(name='Alices stream', creator_id=alice_id, movie_id=self.movie_id)
        (stream_id,) = self.addItems(stream) # pylint: disable=unbalanced-tuple-unpacking
        data = {
            'name': 'Bob stole Alices stream',
        }
        response = self.client.put('/streams/%d' % stream_id, data=data, headers=self.auth_header)
        self.assert403(response)


    def test_get_nonexistent(self):
        response = self.client.get('/streams/7654')
        self.assert404(response)


    def test_get_private_restricted(self):
        response = self.client.get('/streams/%d' % self.p_str_id)
        self.assert401(response)


    def test_get_private_stream_entries_restricted(self):
        response = self.client.get('/streams/%d/entries' % self.p_str_id)
        self.assert401(response)


    def test_delete_nonexistent(self):
        response = self.client.delete('/streams/654', headers=self.auth_header)
        self.assert404(response)


    def test_put_nonexistent(self):
        stream = {
            'name': "Who's that?",
        }
        response = self.client.put('/streams/6543', data=stream, headers=self.auth_header)
        self.assert404(response)


    def test_invalid_put(self):
        stream = {
            'id': self.stream_id,
            'name': '',
        }
        response = self.client.put('/streams/%d' % self.stream_id, data=stream, headers=self.auth_header)
        self.assertValidClientError(response)


    def test_create_stream(self):
        data = {
            'name': 'FactChecker',
        }
        response = self.client.post('/movies/%d/createStream' % self.movie_id, data=data, headers=self.auth_header)
        self.assertValidCreate(response, object_name='stream')
        with self.app.test_request_context():
            streams = Stream.query.all()
            self.assertEqual(len(streams), 3)


    def test_publish_public_stream(self):
        response = self.client.post('/streams/%d/publish' % self.stream_id, headers=self.auth_header)
        self.assert400(response)


    def test_publish_stream(self):
        response = self.client.post('/streams/%d/publish' % self.p_str_id, headers=self.auth_header)
        self.assert200(response)
        with self.app.test_request_context():
            movie = Movie.query.get(self.movie_id)
            self.assertEqual(movie.number_of_streams, 2)
            stream = Stream.query.get(self.p_str_id)
            self.assertTrue(stream.public)


    def test_publish_restricted(self):
        response = self.client.post('/streams/%d/publish' % self.p_str_id)
        self.assert401(response)

        # create other user
        with self.app.test_request_context():
            alice = User(username='alice', email='alice@example.com', password='alicepw')
            alice_id, = self.addItems(alice)
            alice_auth_header = {'Authorization': 'Token %s' % User.query.get(alice_id).get_auth_token()}
        response = self.client.post('/streams/%d/publish' % self.p_str_id, headers=alice_auth_header)
        self.assert403(response)


    def test_unpublish(self):
        response = self.client.post('/streams/%d/unpublish' % self.stream_id, headers=self.auth_header)
        self.assert200(response)
        with self.app.test_request_context():
            movie = Movie.query.get(self.movie_id)
            self.assertEqual(movie.number_of_streams, 0)
            stream = Stream.query.get(self.stream_id)
            self.assertFalse(stream.public)


    def test_unpublish_restricted(self):
        response = self.client.post('/streams/%d/unpublish' % self.stream_id)
        self.assert401(response)

        # create other user
        with self.app.test_request_context():
            alice = User(username='alice', email='alice@example.com', password='alicepw')
            alice_id, = self.addItems(alice)
            alice_auth_header = {'Authorization': 'Token %s' % User.query.get(alice_id).get_auth_token()}
        response = self.client.post('/streams/%d/unpublish' % self.stream_id, headers=alice_auth_header)
        self.assert403(response)


    def test_create_invalid(self):
        data = {
            # missing name
        }
        response = self.client.post('/movies/%d/createStream' % self.movie_id, data=data, headers=self.auth_header)
        self.assertValidClientError(response)
        with self.app.test_request_context():
            movie = Movie.query.get(self.movie_id)
            self.assertEqual(movie.number_of_streams, 1) # should still be only 1


    def test_stream_create_restricted(self):
        data = {
            'name': 'FactChecker',
        }
        response = self.client.post('/movies/%d/createStream' % self.movie_id, data=data)
        self.assert401(response)


class StreamEntryFetchTest(TestCaseWithTempDB, AuthenticatedUserMixin):

    def setUp(self):
        self.authenticate()
        movie = Movie(
            title='Avatar',
            external_id='imdb:tt0499549',
        )
        stream = Stream(name='DurationNotifier', movie=movie, creator=self.user, public=True)
        self.stream_id, _ = self.addItems(stream, movie)
        for i in range(20):
            entry = Entry(
                entry_point_in_ms=i*60*1000,
                title='<h1>Title</h1>',
                content_type='text',
                content='{"text":"We\'re now at %d minutes into the movie."}' % i, stream=stream)
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
