# pylint: disable=attribute-defined-outside-init

from marvin import create_app, db

from os import path

import os
import tempfile
import ujson as json
import unittest

class MarvinBaseTestCase(unittest.TestCase):

    response_code_helpers = (
        200,
        201,
        400,
        403,
        404,
    )

    def __call__(self, result=None, **kwargs):
        """ Do setup here, so that we don't have to do super() calls in every subclass. """
        try:
            self._pre_setup()
            super(MarvinBaseTestCase, self).__call__(result)
        finally:
            self._post_teardown()


    def _pre_setup(self):
        """ Make sure to remove any envvars that might affect test runs. """
        for response_code in self.response_code_helpers:
            self.__dict__['assert%s' % response_code] = self._assert_status_factory(response_code)
        self._original_config_file_from_envvar = os.environ.get('MARVIN_CONFIG_FILE')
        if 'MARVIN_CONFIG_FILE' in os.environ:
            del os.environ['MARVIN_CONFIG_FILE']


    def _post_teardown(self):
        """ Restore any envvars we tampered with. """
        if self._original_config_file_from_envvar:
            os.environ['MARVIN_CONFIG_FILE'] = self._original_config_file_from_envvar


    def assert_status(self, response, status):
        self.assertEqual(response.status_code, status)


    def _assert_status_factory(self, code):
        """ Create the assertXX helpers. They will all check for a status code,
        and some other properties to verify that it's a good response, like that
        it can be decoded to json and contains the correct Content-Type header
        and stuff like that.

        Any keyword arguments passed will be passed along to assertValidResponse.

        :returns: The JSON data of the response.
        """
        def _assert_status(response, **kwargs):
            self.assert_status(response, code)
            json_response = self.assertValidResponse(response, **kwargs)
            return json_response

        return _assert_status


    def assertValidResponse(self, response, mimetype='application/json'):
        """ Checks that the response is generelly good.

        More specifically, will check that the response:
        * Has a Content-Type header of 'application/json' (or anything overridden by the mimetype parameter)
        * Can be decoded to json
        """
        self.assertEqual(response.headers['content-type'], mimetype, "The response should have a " +
            "Content-Type header '%s' (was '%s')" % (mimetype, response.headers['content-type']))
        if mimetype == 'application/json':
            json_response = json.loads(response.data)
            self.assertTrue(len(json_response.keys()) >= 1, "The response should carry some data")
            return json_response
        else:
            return response.data

    def assertValidClientError(self, response, expected_errors=1):
        """ Check that the response is a good reply to a invalid request.

        More specifically, will verify that the request:
        * Has status code 400
        * Contains a message to the user
        * Contains a list of **all** the errors the client did (specify number expected with
            the :param expected_errors:)

        :returns: The JSON data from the response.
        """
        self.assert400(response)
        json_response = self.assertValidResponse(response)
        self.assertTrue('msg' in json_response, "Responses to client errors should always contain a message " +
            "describing the problem")
        self.assertTrue(len(json_response['msg']) > 20, "Responses to client errors should have a decent " +
            "explanation of the problem. Was: '%s'" % json_response['msg'])
        self.assertTrue('errors' in json_response, "Responses to client errors should always contain a list of the" +
            "errors performed")
        self.assertEqual(len(json_response['errors']), expected_errors, "The number of errors in the response " +
            "did not equal what you expected. The errors were: \n%s" %
            '\n'.join('%s: %s' % (key, val) for key, val in json_response['errors'].items()))
        return json_response


    def assertValidCreate(self, response, object_name):
        """ Check that the response is a good reply for creating new objects.

        More specifically, will verify that the request:
        * Has status code 201
        * Contains both a `msg` and the resulting object (under the key passed by ``object_name``)
        * That the resulting object has an href field that can be used for subsequent requests

        :returns: The JSON data from the reponse.
        """
        self.assert201(response)
        json_response = self.assertValidResponse(response)
        self.assertTrue('msg' in json_response, "Responses to create requests should contain a short confimation " +
            "message to the user.")
        self.assertTrue(len(json_response['msg']) > 10)
        self.assertTrue(object_name in json_response, "Responses to object creation requests should contain the " +
            "created object (keyed '%s')" % object_name)
        self.assertTrue('href' in json_response[object_name], "Reponses to object creation requests must contain " +
            "the href of the new object")
        return json_response


class TestCaseWithTempDB(MarvinBaseTestCase):
    """ Inherit from this TestCase if you're doing anything that requires a test
    database. Remember to call super() if you override setUp and/or tearDown.
    """

    def _pre_setup(self):
        super(TestCaseWithTempDB, self)._pre_setup()
        self.tmp_config = tempfile.NamedTemporaryFile(delete=False)
        self.tmp_config.write('\n'.join([
            "SQLALCHEMY_DATABASE_URI = 'sqlite:///../tmptestdb.sqlite'",
            "CELERY_BROKER_URL = 'amqp://'",
            "TESTING = True",
            "SECRET_KEY = 'supersecret'",
            "LOG_CONF_PATH = r'%s'" % path.abspath(path.join(path.dirname(__file__), 'test_log_conf.yaml')),
            ]).encode('utf-8')
        )
        self.tmp_config.close()
        os.environ['MARVIN_CONFIG_FILE'] = self.tmp_config.name
        self.app = create_app()
        self.client = self.app.test_client()
        with self.app.test_request_context():
            db.create_all()


    def _post_teardown(self):
        os.remove(self.tmp_config.name)
        db.session.remove()
        os.remove('../tmptestdb.sqlite')
        super(TestCaseWithTempDB, self)._post_teardown()


    def addItems(self, *args):
        """ Adds all items passed to the database. """
        result_ids = []
        with self.app.test_request_context():
            for item in args:
                db.session.add(item)
            db.session.commit()
            for item in args:
                result_ids.append(item.id)
        return result_ids
