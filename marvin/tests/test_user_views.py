from marvin.models import User
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
        self.bob_id, self.alice_id = self.addItems(bob, alice)
        with self.app.test_request_context():
            self.bob_auth_header = {'authorization': 'Token %s' % User.query.get(self.bob_id).get_auth_token()}


    def test_restricted_profile(self):
        response = self.client.get('/users/%d' % self.alice_id, headers=self.bob_auth_header)
        self.assert403(response)


    def test_access_to_own_profile(self):
        response = self.client.get('/users/%d' % self.bob_id, headers=self.bob_auth_header)
        self.assert200(response)


    def test_login_view(self):
        for identifier in ('bob', 'bob@company.com'):
            response = self.client.post('/login', data={'identifier': identifier, 'password': 'sesamsesam'})
            json_response = self.assert200(response)
            self.assertTrue('auth_token' in json_response)
