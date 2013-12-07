"""
    marvin.permissions
    ~~~~~~~~~~~~~~~~~~

    Permissions used around marvin.

"""

from flask import g
from flask.ext.principal import identity_changed, UserNeed

@identity_changed.connect
def on_identity_loaded(sender, identity): # pylint: disable=unused-argument
    """ When an identify is loaded, initialize it with it's permissions. """

    identity.user = g.user

    # Add the userneed
    identity.provides.add(UserNeed(g.user.id))
