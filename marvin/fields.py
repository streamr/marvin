"""
    marvin.fields
    ~~~~~~~~~~~~~~~~~

    Some custom form field types used by marvin.

"""

from wtforms import widgets
from wtforms.fields import Field
import ujson as json


class JSONField(Field):
    """ A field that validates and processes JSON input. """
    widget = widgets.TextInput()

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = json.loads(valuelist[0])
                # don't accept anything else than javascript objects (like lists, strings, etc)
                if not isinstance(self.data, dict):
                    raise ValueError
            except ValueError:
                self.data = None
                raise ValueError('Not valid JSON.')
        else:
            self.data = None
