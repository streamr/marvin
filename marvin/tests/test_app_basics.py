from marvin import create_app
from marvin.tests import MarvinBaseTestCase

from mock import MagicMock, patch
from nose.tools import raises

import os
import tempfile

class AppCreationTest(MarvinBaseTestCase):

    def setUp(self):
        self.config_file = tempfile.NamedTemporaryFile(delete=False)
        self.config_file.write('\n'.join([
            'OTHER_CONFIG = "bar"',
            'TESTING = True',
            'CELERY_BROKER_URL = "amqp://"',
        ]).encode('utf-8'))
        self.config_file.close()
        os.environ['MARVIN_CONFIG_FILE'] = self.config_file.name


    def tearDown(self):
        os.remove(self.config_file.name)
        del os.environ['MARVIN_CONFIG_FILE']


    def test_create_app(self):
        app = create_app(MY_CONFIG_VALUE='foo')
        self.assertEqual(app.config['MY_CONFIG_VALUE'], 'foo')


    def test_create_app_with_config_file(self):
        app = create_app(self.config_file.name)
        self.assertEqual(app.config['OTHER_CONFIG'], 'bar')


    def test_create_app_both(self):
        app = create_app(self.config_file.name, EXTRA_PARAM='baz')
        self.assertEqual(app.config['OTHER_CONFIG'], 'bar')
        self.assertEqual(app.config['EXTRA_PARAM'], 'baz')


    def test_app_with_log_config(self):
        log_conf = tempfile.NamedTemporaryFile(delete=False)
        log_conf.write('version: 1'.encode('utf-8'))
        log_conf.close()
        app = create_app(LOG_CONF_PATH=log_conf.name)
        self.assertIsNotNone(app)
        os.remove(log_conf.name)


    def test_error_handler_500(self):
        log_conf = tempfile.NamedTemporaryFile(delete=False)
        log_conf.write('version: 1'.encode('utf-8'))
        log_conf.close()

        # test both API and blueprint error handlers
        for url, patchpoint in [('/', 'marvin.views.stats.stats_main'),
                                ('/movies', 'marvin.views.movies.AllMoviesView.get')]:
            logger = MagicMock()

            # pylint: disable=multiple-statements
            with patch('marvin.utils._logger', logger), patch(patchpoint, lambda s: 1/0):
                app = create_app(
                    TESTING=False,
                    LOG_CONF_PATH=log_conf.name,
                )
                response = app.test_client().get(url)
                self.assert_status(response, 500)
                self.assertEqual(len(logger.exception.mock_calls), 1)
        os.remove(log_conf.name)


class AppCreationWithoutTestMode(MarvinBaseTestCase):

    @raises(ValueError)
    def test_app_with_missing_log_config(self): # pylint: disable=no-self-use
        create_app()
