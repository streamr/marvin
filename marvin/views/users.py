"""
    marvin.views.users
    ~~~~~~~~~~~~~~~~~~~~

    CRU endpoints for users.

"""
# pylint: disable=no-self-use

from .. import db
from ..models import User, UserForm, UserLoginForm
from ..permissions import login_required
from ..security import is_correct_pw

from flask.ext.restful import Resource
from flask.ext.principal import UserNeed, Permission

class CreateUserView(Resource):
    """ Create endpoint for users. """

    def post(self):
        """ Create new user. """
        form = UserForm()
        if form.validate_on_submit():
            user = User(password=form.password.data)
            form.populate_obj(user)
            db.session.add(user)
            db.session.commit()
            return {
                'msg': 'User created',
                'user': user.to_json(),
                'auth_token': user.get_auth_token(),
            }, 201
        return {
            'msg': 'Data did not validate.',
            'errors': form.errors,
        }, 400


class LoginView(Resource):
    """ Endpoint for creating an auth_token. """

    def post(self):
        """ Create new auth_token. """
        form = UserLoginForm()
        if form.validate_on_submit():
            user = (User.query.filter(User.username==form.identifier.data).first()
                or User.query.filter(User.email==form.identifier.data).first())
            if user:
                if is_correct_pw(form.password.data, user.password_hash):
                    return {
                        'auth_token': user.get_auth_token(),
                    }
            return {
                'msg': 'Incorrect username or password',
            }, 401
        return {
            'msg': 'Data did not validate',
            'errors': form.errors,
        }, 400


class UserDetailView(Resource):
    """ Read/Update endpoint for users. """

    @login_required
    def get(self, user_id):
        """ Get details for a given user. """
        view_permission = Permission(UserNeed(user_id))
        if view_permission.can():
            user = User.query.get_or_404(user_id)
            return {
                'user': user.to_json(include_personal_data=True),
            }
        else:
            return {
                'msg': 'You do not have the sufficient privileges to view the details of this user',
            }, 403
