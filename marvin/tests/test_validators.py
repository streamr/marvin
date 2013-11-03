from marvin.validators import fk_exists

from mock import Mock
from wtforms.validators import ValidationError

import unittest

class FKExistsValidatorTest(unittest.TestCase):

    def test_object_fk_exists_on_valid_object(self): # pylint: disable=no-self-use
        model = Mock()
        model.query = {
            '1': 'An object with id 1'
        }
        field = Mock()
        field.data = '1'
        validator = fk_exists(model)
        validator(None, field) # Should not blow up


    def test_fk_exists_invalid_object(self):
        model = Mock()
        model.query = {} # No objects present
        model.__tablename__ = 'mymodel'
        field = Mock()
        field.data = '1'
        validator = fk_exists(model)
        self.assertRaises(ValidationError, validator, None, field)
