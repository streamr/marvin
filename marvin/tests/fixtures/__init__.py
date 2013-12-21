"""
    marvin.tests.fixtures
    ~~~~~~~~~~~~~~~~~~~~~

    This package contains fixtures that can be used for testing or quickly firing up a test
    instance with some test data.

"""

from . import complete as COMPLETE

from marvin import db

import re

#: The regex to check whether a module level variable should be added or not. Ignores everything that starts with
#: capital letters, as that's usually the model objects (like User, Movie, Stream, etc)
_FIXTURE_ITEM_FILTER = re.compile('[a-z][a-z0-9_]*')

def load(app, module):
    """ Loads all the given items into the database used by app.

    :param app: The app to use.
    :param items: A list of items to use. Many predefined lists exists in the `marvin.tests.fixtures` package.
    """
    items = _get_items_in_module(module)
    with app.test_request_context():
        db.session.add_all(items)
        db.session.commit()

def _get_items_in_module(module):
    # Make sure we get fresh objects, since SQLAlchemy doesn't add the same objects twice:
    reload(module)
    return [item for item_name, item in vars(module).items() if _FIXTURE_ITEM_FILTER.match(item_name)]
