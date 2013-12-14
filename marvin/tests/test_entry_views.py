from marvin.models import Movie, Stream, Entry, User
from marvin.tests import TestCaseWithTempDB, AuthenticatedUserMixin

class EntryDetailViewTest(TestCaseWithTempDB, AuthenticatedUserMixin):

    def setUp(self):
        self.authenticate()
        movie = Movie(
            title='Avatar',
            external_id='imdb:tt0499549',
        )
        stream = Stream(name='CinemaSins', movie=movie, creator=self.user)
        too_big_tv = Entry(
            entry_point_in_ms=3*60*1000,
            stream=stream,
            title='<h1>Title</h1>',
            content_type='text',
            content='''{
                "text": "<p>Do you really need a wall-sized TV when you're sitting three inches from it?</p>"
            }''',
        )
        cardboard_coffin = Entry(
            entry_point_in_ms=5*60*1000,
            stream=stream,
            title='<h1>Title</h1>',
            content_type='text',
            content='''{
                "text": "<p>Why are the coffins of the future made out of cardboard?</p>"
            }''',
        )
        self.stream_id, self.tv_id, self.cardboard_id, self.movie_id = self.addItems(
            stream, too_big_tv, cardboard_coffin, movie)


    def test_entry_detail_view(self):
        response = self.client.get('/entries/%d' % self.tv_id)
        json_response = self.assert200(response)
        self.assertEqual(json_response['entry']['entry_point_in_ms'], 180000)
        self.assertTrue('wall-sized TV' in json_response['entry']['content']['text'])


    def test_update_nonexistent_entry(self):
        entry = {
            'entry_point_in_ms': 3*60*1000,
            'title': '<h1>Title</h1>',
            'content': '<p>This is weird</p>',
        }
        response = self.client.put('/entries/65432', data=entry)
        self.assert404(response)


    def test_update_entry(self):
        entry = {
            'id': self.tv_id,
            'entry_point_in_ms': 2*60*1000, # We change the entry point
            'title': '<h1>Title</h1>',
            'content_type': 'text',
            'content': '{"text":"<p>Do you really need a wall-sized TV when you\'re sitting three inches from it?</p>"}',
        }
        response = self.client.put('/entries/%d' % self.tv_id, data=entry)
        json_response = self.assert200(response)
        self.assertEqual(json_response['msg'], 'Entry updated.')
        self.assertFalse('errors' in json_response)
        with self.app.test_request_context():
            new_entry = Entry.query.get(self.tv_id)
            self.assertEqual(new_entry.content,
                '{"text":"<p>Do you really need a wall-sized TV when you\'re sitting three inches from it?</p>"}')


    def test_update_invalid(self):
        entry = {
            'id': self.tv_id,
            'entry_point_in_ms': -1, # Invalid entry point,
            'title': 'Fancy title',
            'content': 'Too large TV',
        }
        response = self.client.put('/entries/%d' % self.tv_id, data=entry)
        self.assert400(response)


    def test_delete_entry(self):
        response = self.client.delete('/entries/%d' % self.tv_id)
        json_response = self.assert200(response)
        self.assertEqual(json_response['msg'], 'Entry deleted.')
        with self.app.test_request_context():
            self.assertEqual(len(Entry.query.all()), 1)


    def test_create_new_entry(self):
        entry = {
            'entry_point_in_ms': 10*60*1000,
            'title': '<h1>Title</h1>',
            'content_type': 'text',
            'content': '{"text": "<p>Yes, a planet full of trees has no oxygen.</p>"}',
        }
        response = self.client.post('/streams/%s/createEntry' % self.stream_id, data=entry, headers=self.auth_header)
        self.assertValidCreate(response, object_name='entry')


    def test_create_invalid_json_shoukd_fail(self):
        entry = {
            'entry_point_in_ms': 1000,
            'content_type': 'text',
            'content': '{"text":}', # invalid JSON
            'title': 'Bad JSON',
        }
        response = self.client.post('/streams/%s/createEntry' % self.stream_id, data=entry, headers=self.auth_header)
        json_response = self.assert400(response)
        self.assertEqual(len(json_response['errors']), 1)
        self.assertTrue(u'Not valid JSON.' in json_response['errors']['content'])


    def test_create_invalid_entry(self):
        entry = {
            'entry_point_in_ms': -1, # entry points must be positive
            'content': '{"text": "<p>Ripleys gotten old</p>"}',
            # does not include title
            # does not include content_type
        }
        response = self.client.post('/streams/%s/createEntry' % self.stream_id, data=entry, headers=self.auth_header)
        self.assertValidClientError(response, expected_errors=3)


    def test_create_entry_to_invalid_stream(self):
        entry = {
            'entry_point_in_ms': 5*60*1000,
            'title': '<h1>Title</h1>',
            'content': 'This is bad.',
        }
        response = self.client.post('/streams/876543/createEntry', data=entry, headers=self.auth_header)
        self.assert404(response)


    def test_create_entry_with_manual_id(self):
        entry = {
            'id': 6543, #should not be able to assign ID manually,
            'entry_point_in_ms': 9*60*1000,
            'title': '<h1>Title</h1>',
            'content_type': 'text',
            'content': '{"text": "<p>Valid content here.</p>"}',
        }
        response = self.client.post('/streams/%s/createEntry' % self.stream_id, data=entry, headers=self.auth_header)
        # should ignore non-accepted fields
        self.assertValidCreate(response, object_name='entry')
        with self.app.test_request_context():
            saved_entry = Entry.query.filter_by(entry_point_in_ms=9*60*1000).first()
            self.assertNotEqual(saved_entry.id, entry['id'])


    def test_create_entry_restricted(self):
        entry = {
            'entry_point_in_ms': 10*60*1000,
            'title': '<h1>Title</h1>',
            'content': '<p>Yes, a planet full of trees has no oxygen.</p>',
        }
        response = self.client.post('/streams/%d/createEntry' % self.stream_id, data=entry)
        self.assert401(response)


    def test_create_entry_to_others_stream(self):
        with self.app.test_request_context():
            alice = User(username='alice', email='alice@example.com', password='alicepw')
            alices_stream = Stream(name='Alices stream', movie_id=self.movie_id, creator=alice)
            _, alices_stream_id = self.addItems(alice, alices_stream) # pylint: disable=unbalanced-tuple-unpacking
        entry = {
            'entry_point_in_ms': 10*60*1000,
            'title': '<h1>Title</h1>',
            'content': '<p>Yes, a planet full of trees has no oxygen.</p>',
        }
        response = self.client.post('/streams/%d/createEntry' % alices_stream_id, data=entry, headers=self.auth_header)
        self.assert403(response)
