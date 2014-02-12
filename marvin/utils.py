"""
    marvin.utils
    ~~~~~~~~~~~~

    A collection of utilities that might be handy in several places in the marvin code.

"""

from flask import make_response, request
from flask.ext.restful import Api
from logging import getLogger
from werkzeug.exceptions import HTTPException

import textwrap
import ujson

_logger = getLogger('marvin.utils')


class ApiBase(Api):
    """ Base API class used to add some extra functionality to Flask-RESTful. """
    # pylint: disable=super-on-old-class

    def __init__(self, *args, **kwargs):
        super(ApiBase, self).__init__(*args, **kwargs)
        self.representations = {
            'application/json': _fastjson,
        }

    def handle_error(self, exception):
        """ Override handle_error to make sure the exception is handled by the correct logger. """
        # Don't do any special logging of client side errors
        if not (isinstance(exception, HTTPException) and (400 <= exception.code < 500)):
            generic_error_handler(exception)
        return super(ApiBase, self).handle_error(exception)


def _fastjson(data, code, headers=None):
    """ Replace the default json serializer with one based on ujson. """
    response = make_response(ujson.dumps(data), code)
    response.headers.extend(headers or {})
    return response


def error_handler(error):
    """ Handles errors outside the API, ie in blueprints. """
    generic_error_handler(error)
    response_data = {
        'msg': "Oops, server fault! We'll try to fix it ASAP, hang tight!",
    }
    response = _fastjson(response_data, 500, {'Content-Type': 'application/json'})
    return response


def generic_error_handler(exception):
    """ Log exception to the standard marvin logger. """
    log_msg = textwrap.dedent("""Error occured!
        Path:                 %s
        Params:               %s
        HTTP Method:          %s
        Client IP Address:    %s
        User Agent:           %s
        User Platform:        %s
        User Browser:         %s
        User Browser Version: %s
        HTTP Headers:         %s
        Exception:            %s
        """ % (
            request.path,
            request.values,
            request.method,
            request.remote_addr,
            request.user_agent.string,
            request.user_agent.platform,
            request.user_agent.browser,
            request.user_agent.version,
            request.headers,
            exception
        )
    )
    #sysout seems a bit eradic for the loggers, so if any tests fail, you might want to uncomment these lines
    # print(log_msg)
    # import traceback
    # traceback.print_exc()
    _logger.exception(log_msg)


def teardown_appcontext(error):
    """ Commits the session if no error has occured, otherwise rollbacks. """
    from . import db # Import down here to avoid circular import
    if error is None:
        try:
            db.session.commit()
        except Exception: # pylint: disable=broad-except
            # Whoops, a little too late too modify the response, but rollback the session
            # and make sure the exception is logged
            db.session.rollback()
            _logger.exception('Exception happened during teardown commit.')
    else:
        # We have an exception, but it has probably already been handled by the approriate handlers,
        # so just rollback the session and ignore the error
        db.session.rollback()
    db.session.remove()
