"""
    marvin.permissions
    ~~~~~~~~~~~~~~~~~~

    Permissions used around marvin.

"""

from flask import g
from flask.ext.principal import identity_changed, UserNeed

from functools import wraps


@identity_changed.connect
def on_identity_loaded(sender, identity): # pylint: disable=unused-argument
    """ When an identify is loaded, initialize it with it's permissions. """

    identity.user = g.user

    # Add the userneed
    identity.provides.add(UserNeed(g.user.id))


def login_required(func):
    """ If you decorate a view with this, it will ensure that the current user is
    logged in and authenticated before calling the actual view.

    :param func: The view function to decorate.
    :type func: function
    """

    @wraps(func)
    def decorated_view(*args, **kwargs):
        """ View that only grants access to authenticated users. """
        if g.user.is_authenticated():
            return func(*args, **kwargs)
        else:
            return {
                'msg': 'You must pass an auth_token to be able to access this endpoint',
            }, 401
    return decorated_view
