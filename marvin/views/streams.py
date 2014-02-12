"""
    marvin.views.streams
    ~~~~~~~~~~~~~~~~~~~~

    CRUD endpoints for streams.

"""
# pylint: disable=no-self-use

from .. import db
from ..models import Stream, StreamForm, Entry, Movie
from ..permissions import login_required

from flask import g, request
from flask.ext.principal import UserNeed, Permission
from flask.ext.restful import Resource
from logging import getLogger

_logger = getLogger('marvin.views.streams')


class StreamDetailView(Resource):
    """ RUD interface to streams. """

    def get(self, stream_id):
        """ Get the stream with the given ID. """
        stream = Stream.query.get_or_404(stream_id)
        is_owner = Permission(UserNeed(stream.creator_id))
        if stream.public or is_owner:
            return {
                'stream': stream.to_json(),
            }
        else:
            _logger.warning("Access to private stream was attemped. Stream: %s, user: %s",
                stream.name, g.user)
            return {
                'msg': 'This stream is not public yet.',
            }, 403 if g.user else 401


    @login_required
    def put(self, stream_id):
        """ Update the stream with the given ID. """
        stream = Stream.query.get_or_404(stream_id)
        edit_permission = Permission(UserNeed(stream.creator_id))
        if edit_permission.can():
            form = StreamForm(obj=stream)
            if form.validate_on_submit():
                form.populate_obj(stream)
                return {
                    'msg': 'Stream updated.',
                    'stream': stream.to_json(),
                }
            return {
                'msg': 'Some attributes did not pass validation.',
                'errors': form.errors,
            }, 400
        else:
            return {
                'msg': "You're not allowed to edit this stream"
            }, 403


    @login_required
    def delete(self, stream_id):
        """ Delete the stream with the given ID. """
        stream = Stream.query.get_or_404(stream_id)
        delete_permission = Permission(UserNeed(stream.creator_id))
        if delete_permission.can():
            movie = stream.movie
            movie.number_of_streams -= 1
            db.session.delete(stream)
            db.session.add(movie)
            return {'msg': 'Stream deleted.'}
        else:
            return {
                'msg': "You're not allowed to delete this stream."
            }, 403


class CreateStreamView(Resource):
    """ Create interface for streams. """

    @login_required
    def post(self, movie_id):
        """ Create new stream. """
        form = StreamForm()
        if form.validate_on_submit():
            movie = Movie.query.get_or_404(movie_id)
            stream = Stream(creator=g.user)
            form.populate_obj(stream)
            stream.movie = movie
            db.session.add(stream)
            db.session.add(movie)
            db.session.commit()
            return {
                'msg': 'Stream created',
                'stream': stream.to_json(),
            }, 201
        return {
            'msg': 'Data did not validate.',
            'errors': form.errors,
        }, 400


class StreamEntryView(Resource):
    """ Read endpoint for entries in a stream. """

    def get(self, stream_id):
        """ Get entries for the given stream.

        Respect the following request parameters:

        * ``limit``: Restrict number of entries returned to this amount.
        * ``starttime_gt``: Only return entries that enter after this time, in ms.
        """
        stream = Stream.query.get_or_404(stream_id)
        is_owner = Permission(UserNeed(stream.creator_id))
        if stream.public or is_owner:
            max_number_of_entries = request.args.get('limit', 100)
            starttime_gt = request.args.get('starttime_gt', -1)
            entries = (stream.entries
                .filter(Entry.entry_point_in_ms > starttime_gt)
                .order_by(Entry.entry_point_in_ms.asc())
                .limit(max_number_of_entries))
            return {
                'entries': [entry.to_json() for entry in entries],
            }
        else:
            return {
                'msg': 'This stream is not public yet.',
            }, 403 if g.user else 401


class PublishStreamView(Resource):
    """ Publish the given stream. """

    @login_required
    def post(self, stream_id):
        """ Publish the stream, increase movie's stream count. """
        stream = Stream.query.get_or_404(stream_id)
        if stream.public:
            return {
                'msg': 'This stream has already been published!',
            }, 400
        is_owner = Permission(UserNeed(stream.creator_id))
        if is_owner:
            stream.public = True
            stream.movie.number_of_streams += 1
            db.session.commit()
            return {
                'msg': 'Congratulations! The stream "%s" was published successfully.' % stream.name,
            }
        else:
            return {
                'msg': 'You can only publish your own streams.'
            }, 403


class UnpublishStreamView(Resource):
    """ Unpublish the given stream. """

    @login_required
    def post(self, stream_id):
        """ Unpublish the stream, decrease movie's stream count. """
        stream = Stream.query.get_or_404(stream_id)
        if not stream.public:
            return {
                'msg': "This stream hasn't been published yet!",
            }, 400
        is_owner = Permission(UserNeed(stream.creator_id))
        if is_owner:
            stream.public = False
            stream.movie.number_of_streams -= 1
            db.session.commit()
            return {
                'msg': 'The stream "%s" was removed from public view successfully.' % stream.name,
            }
        else:
            return {
                'msg': 'You can only unpublish your own streams.'
            }, 403
