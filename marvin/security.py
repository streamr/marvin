"""
    marvin.security
    ~~~~~~~~~~~~~~~

    Security-related utilities and tools.

"""

from .utils import generic_error_handler

from itsdangerous import BadData, constant_time_compare, URLSafeSerializer
from flask import abort, current_app, g, request
from flask.ext.principal import identity_changed, Identity

import base64
import os

# Don't require scrypt to be installed in debug mode, since it's hell to compile on windows
try:
    import scrypt
except ImportError: # pragma: no cover
    from hashlib import sha256
    class scrypt(object): # pylint: disable=invalid-name
        """ Faking scrypt using a single sha256 hash if scrypt is not available. """
        @staticmethod
        def hash(password, salt, n, p, r): # pylint: disable=unused-argument,invalid-name
            """ Simulate scrypt.hash in dev mode. """
            if not (current_app.config.get('DEBUG') or current_app.config.get('TESTING')): # pragma: no cover
                raise ValueError("scrypt needs to be configured in production!")
            hasher = sha256()
            hasher.update(password)
            hasher.update(salt)
            return hasher.digest()


def _generate_salt_bytes():
    """ Generate a random bytestring that can be used as a cryptographic salt.

    The resulting bytestring will be approx 88 bytes long, 64 bytes of pure randomness
    and 33% overhead due to base64-encoding the result.
    """
    randomness = os.urandom(64)
    b64encoded = base64.b64encode(randomness)
    bytestring = force_bytes(b64encoded)
    return bytestring


def generate_pw_hash(password):
    """ Hash the given password.

    Return a string in the format ``method$salt$hash``.
    """
    # pylint: disable=invalid-name
    salt = _generate_salt_bytes()
    (N, p, r) = get_system_scrypt_params()
    method = '%s:%d:%d:%d' % ('scrypt', N, p, r)
    password_bytes = password.encode('utf-8')
    pwhash = scrypt.hash(password_bytes, salt, N, p, r)
    return '%s$%s$%s' % (method, salt, base64.b64encode(pwhash))


def get_system_scrypt_params():
    """ Get optimal N, p and r values for this sytem. """
    #FIXME: Hardcoded for now since lead dev is on windows and can't test against working scrypt...
    return (1024, 8, 1)


def force_bytes(string):
    """ Make sure the given argument is an instance of bytes. On python3, this is probably the case,
    but on python2 we have to encode it with an encoding, in this case we'll use utf-8.
    """
    if hasattr(string, 'encode'): # py2
        string = string.encode('utf-8')
    return string


def is_correct_pw(password, password_hash):
    """ Check that the given password hashes to the given password_hash.

    :param password: The password to test
    :param password_hash: A method$salt$hash string we can extract the method and params used in the
        original hashing from.
    """
    # pylint: disable=invalid-name
    method, salt, hashed_pw = password_hash.split('$')
    # For now we only support scrypt hashing, so we can ignore the algorithm,
    # and we know the number of params. This should be rewritten if we want to
    # support other algorithms or variable length params
    (_, N, p, r) = method.split(':')
    password_bytes = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    (N, p, r) = (int(N), int(p), int(r))
    hashed_bytes = scrypt.hash(password_bytes, salt_bytes, N, p, r)
    b64hash = base64.b64encode(hashed_bytes)
    b64hash_bytes = force_bytes(b64hash)
    hashed_pw_bytes = force_bytes(hashed_pw)
    return constant_time_compare(hashed_pw_bytes, b64hash_bytes)


def decode_token_or_400(auth_token):
    """ Decode the given auth_token and return the data dict therein, or fail with a HTTP 400 error. """
    serializer = URLSafeSerializer(current_app.config['SECRET_KEY'])
    try:
        return serializer.loads(auth_token)
    except BadData as ex:
        generic_error_handler(ex)
        abort(400)


def get_user_from_auth_data(auth_data):
    """ Get the user object from the given auth_data. Raises HTTP 401 if token is no longer valid or user doesn't exist
    anymore.
    """
    # Import the user model here to avoid circular imports
    from .models import User
    user = User.query.get(auth_data['i'])
    if user and user.verify_auth_data(auth_data):
        return user
    abort(401)


def get_auth_token_from_header():
    """ Extract the token from a HTTP Authorization header.

    The header is supposed to look be in the format `Authorization: Token <access token>`

    :returns: Auth token from header, or `None` if none was found.
    """
    header = request.headers.get('authorization')
    if header and header.startswith('Token '):
        auth_token = header[6:]
        return auth_token
    return None


def before_request_authentication():
    """ Connect with @app.before_request to authenticate users using the
    `auth_token` request param.

    Assigns a user to `g.user`, AnonymousUser if no auth_token was sent in the request.
    """
    # pylint: disable=protected-access
    from .models import AnonymousUser
    auth_token = get_auth_token_from_header()
    if auth_token:
        data = decode_token_or_400(auth_token)
        user = get_user_from_auth_data(data)
        g.user = user
        identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
    else:
        g.user = AnonymousUser()
