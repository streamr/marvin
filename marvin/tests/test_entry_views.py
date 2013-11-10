from marvin.models import Movie, Stream, Entry
from marvin.tests import TestCaseWithTempDB

class EntryDetailViewTest(TestCaseWithTempDB):

    def setUp(self):
        movie = Movie(
            title='Avatar',
            external_id='imdb:tt0499549',
        )
        stream = Stream(name='CinemaSins', movie=movie)
        too_big_tv = Entry(entry_point_in_ms=3*60*1000, stream=stream,
            content="<p>Do you really need a wall-sized TV when you're sitting three inches from it?</p>")
        cardboard_coffin = Entry(entry_point_in_ms=5*60*1000, stream=stream,
            content="<p>Why are the coffins of the future made out of cardboard?</p>")
        self.stream_id, self.tv_id, self.cardboard_id, _ = self.addItems(stream, too_big_tv, cardboard_coffin, movie)


    def test_entry_detail_view(self):
        response = self.client.get('/entries/%d' % self.tv_id)
        json_response = self.assert200(response)
        self.assertEqual(json_response['entry']['entry_point_in_ms'], 180000)
        self.assertTrue('wall-sized TV' in json_response['entry']['content'])


    def test_update_nonexistent_entry(self):
        entry = {
            'entry_point_in_ms': 3*60*1000,
            'content': '<p>This is weird</p>',
        }
        response = self.client.put('/entries/65432', data=entry)
        self.assert404(response)


    def test_update_entry(self):
        entry = {
            'id': self.tv_id,
            'entry_point_in_ms': 2*60*1000, # We change the entry point
            'content': "<p>Do you really need a wall-sized TV when you're sitting three inches from it?</p>",
        }
        response = self.client.put('/entries/%d' % self.tv_id, data=entry)
        json_response = self.assert200(response)
        self.assertEqual(json_response['msg'], 'Entry updated.')
        self.assertFalse('errors' in json_response)
        with self.app.test_request_context():
            new_entry = Entry.query.get(self.tv_id)
            self.assertEqual(new_entry.content,
                "<p>Do you really need a wall-sized TV when you're sitting three inches from it?</p>")


    def test_delete_entry(self):
        response = self.client.delete('/entries/%d' % self.tv_id)
        json_response = self.assert200(response)
        self.assertEqual(json_response['msg'], 'Entry deleted.')
        with self.app.test_request_context():
            self.assertEqual(len(Entry.query.all()), 1)


    def test_create_new_entry(self):
        entry = {
            'entry_point_in_ms': 10*60*1000,
            'content': '<p>Yes, a planet full of trees has no oxygen.</p>',
            'stream_id': self.stream_id,
        }
        response = self.client.post('/entries', data=entry)
        self.assertValidCreate(response, object_name='entry')


    def test_create_invalid_entry(self):
        entry = {
            'entry_point_in_ms': -1, # entry points must be positive
            'content': '<p>Ripleys gotten old</p>',
            # does not include stream_id
        }
        response = self.client.post('/entries', data=entry)
        self.assertValidClientError(response, expected_errors=2)


    def test_create_entry_to_invalid_stream(self):
        entry = {
            'entry_point_in_ms': 5*60*1000,
            'content': 'This is bad.',
            'stream_id': -1,
        }
        response = self.client.post('/entries', data=entry)
        json_response = self.assertValidClientError(response)
        self.assertEqual(json_response['errors']['stream_id'][0], 'No stream with id -1 found.')


    def test_create_entry_with_manual_id(self):
        entry = {
            'id': 6543, #should not be able to assign ID manually,
            'entry_point_in_ms': 9*60*1000,
            'content': '<p>Valid content here.</p>',
            'stream_id': self.stream_id,
        }
        response = self.client.post('/entries', data=entry)
        # should ignore non-accepted fields
        self.assertValidCreate(response, object_name='entry')
        with self.app.test_request_context():
            saved_entry = Entry.query.filter_by(entry_point_in_ms=9*60*1000).first()
            self.assertNotEqual(saved_entry.id, entry['id'])
