from marvin import create_app

import unittest

class AppCreationTest(unittest.TestCase):

    def test_create_app(self):
        app = create_app(MY_CONFIG_VALUE='foo')
        self.assertEqual(app.config['MY_CONFIG_VALUE'], 'foo')
