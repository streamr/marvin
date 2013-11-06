from marvin import create_app, init_db
from marvin.tests import MarvinBaseTestCase

import os
import tempfile

class AppCreationTest(MarvinBaseTestCase):

    def setUp(self):
        self.config_file = tempfile.NamedTemporaryFile(delete=False)
        self.config_file.write('OTHER_CONFIG = "bar"\nTESTING = True'.encode('utf-8'))
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


    def test_init_db(self):
        app = create_app(SQLALCHEMY_DATABASE_URI='sqlite:///../nonexistent.db')
        init_db(app)
        self.assertTrue(os.path.exists('../nonexistent.db'))
        os.remove('../nonexistent.db')


    def test_app_with_log_config(self):
        log_conf = tempfile.NamedTemporaryFile(delete=False)
        log_conf.write('version: 1'.encode('utf-8'))
        log_conf.close()
        app = create_app(LOG_CONF_PATH=log_conf.name)
        self.assertTrue(app is not None)
        os.remove(log_conf.name)


    def test_app_missing_log_config_in_debug(self):
        app = create_app(DEBUG=True)
        self.assertTrue(app is not None)


class AppCreationWithoutTestMode(MarvinBaseTestCase):

    def test_app_with_missing_log_config(self):
        app = create_app()
        self.assertIsNone(app)
