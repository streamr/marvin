from marvin import create_app, init_db

import os
import tempfile
import unittest

class AppCreationTest(unittest.TestCase):

    def setUp(self):
        self.config_file = tempfile.NamedTemporaryFile(delete=False)
        self.config_file.write('OTHER_CONFIG = "bar"'.encode('utf-8'))
        self.config_file.close()


    def tearDown(self):
        os.remove(self.config_file.name)


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
