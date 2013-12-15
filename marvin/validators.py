"""
    marvin.validators
    ~~~~~~~~~~~~~~~~~

    Some validators that can be used to validate incoming form data.

"""

from wtforms import ValidationError

import ujson as json


class JSONValidator(object):
    """ Validates that the data is valid JSON, and that it represents a JS object (python dict). """

    def __call__(self, form, field):
        try:
            data = json.loads(field.data)
            if not isinstance(data, dict):
                raise ValidationError('Not valid JSON.')
        except ValueError:
            raise ValidationError('Not valid JSON.')
