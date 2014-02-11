from marvin.models import User, Stream, Movie
from marvin.tests import TestCaseWithTempDB

class UserCreationTest(TestCaseWithTempDB):

    def test_new_user(self):
        user = {
            'username': 'bob',
            'password': 'sesamsesam',
            'email': 'bob@company.com',
        }
        response = self.client.post('/users', data=user)
        json_response = self.assertValidCreate(response, object_name='user')
        self.assertTrue('auth_token' in json_response)
        with self.app.test_request_context():
            self.assertEqual(User.query.count(), 1)


class UserAccessRestrictionTest(TestCaseWithTempDB):

    def setUp(self):
        with self.app.app_context():
            bob = User(username='bob', email='bob@company.com', password='sesamsesam')
            alice = User(username='alice', email='alice@gmail.com', password='123456')
        goldeneye = Movie(
            title='GoldenEye',
            external_id='imdb:tt0113189',
        )
        stream = Stream(
            name='Bond cars',
            creator=alice,
            movie=goldeneye,
            public=True,
        )
        private_stream = Stream(
            name='Uncompleted Bond guns',
            creator=alice,
            movie=goldeneye,
            public=False,
        )
        self.bob_id, self.alice_id = self.addItems(bob, alice, stream, goldeneye, private_stream)[:2]
        with self.app.test_request_context():
            self.bob_auth_header = {'authorization': 'Token %s' % User.query.get(self.bob_id).get_auth_token()}
            self.alice_auth_header = {'authorization': 'Token %s' % User.query.get(self.alice_id).get_auth_token()}


    def test_restricted_profile(self):
        response = self.client.get('/users/%d' % self.alice_id, headers=self.bob_auth_header)
        json_response = self.assert200(response)

        # Should not have access to sensitive data
        self.assertFalse('email' in json_response['user'])
        self.assertFalse('signup_date' in json_response['user'])

        # username is public tho
        self.assertTrue('username' in json_response['user'])
        self.assertTrue(json_response['user']['username'], 'alice')

        # and public streams
        self.assertEqual(len(json_response['user']['streams']), 1)
        self.assertEqual(json_response['user']['streams'][0]['name'], 'Bond cars')


    def test_access_to_own_profile(self):
        response = self.client.get('/users/%d' % self.alice_id, headers=self.alice_auth_header)
        json_response = self.assert200(response)

        # owner should be able to see email
        self.assertTrue('email' in json_response['user'])

        # and private streams
        self.assertEqual(len(json_response['user']['streams']), 2)


    def test_login_view(self):
        for identifier in ('bob', 'bob@company.com'):
            response = self.client.post('/login', data={'identifier': identifier, 'password': 'sesamsesam'})
            json_response = self.assert200(response)
            self.assertTrue('auth_token' in json_response)
