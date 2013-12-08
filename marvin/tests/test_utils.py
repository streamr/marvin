from marvin.tests import TestCaseWithTempDB, AuthenticatedUserMixin
from marvin.utils import get_auth_token_from_header, before_request_authentication

from flask import g
from werkzeug.exceptions import BadRequest

class AuthorizationTest(TestCaseWithTempDB):

    def test_get_auth_token_from_request_header(self):
        header = {
            'Authorization': 'Token deadbeef'
        }
        with self.app.test_request_context(headers=header):
            parsed_token = get_auth_token_from_header()
            self.assertEqual(parsed_token, 'deadbeef')


    def test_get_auth_token_missing_header(self):
        with self.app.test_request_context():
            parsed_token = get_auth_token_from_header()
            self.assertIsNone(parsed_token)


    def test_before_request_handler_anonymous(self):
        with self.app.test_request_context():
            before_request_authentication()
            self.assertFalse(g.user.is_authenticated())


    def test_before_request_handler_with_bad_auth(self):
        header = {
            'Authorization': 'Token deadbeef',
        }
        with self.app.test_request_context(headers=header):
            with self.assertRaises(BadRequest):
                before_request_authentication()



class GoodAuthTest(TestCaseWithTempDB, AuthenticatedUserMixin):

    def setUp(self):
        self.authenticate()


    def test_before_request_handler_successful_auth(self):
        with self.app.test_request_context(headers=self.auth_header):
            before_request_authentication()
            self.assertTrue(g.user.is_authenticated())
            self.assertEqual(g.user.username, 'bob')
