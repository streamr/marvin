"""
    marvin.views.streams
    ~~~~~~~~~~~~~~~~~~~~

    CRUD endpoints for streams.

"""
# pylint: disable=no-self-use

from .. import db
from ..models import Stream, StreamForm

from flask.ext.restful import Resource

class StreamDetailView(Resource):
    """ RUD interface to streams. """

    def get(self, stream_id):
        """ Get the stream with the given ID. """
        stream = Stream.query.get_or_404(stream_id)
        return {
            'stream': stream.to_json(),
        }


    def put(self, stream_id):
        """ Update the stream with the given ID. """
        stream = Stream.query.get_or_404(stream_id)
        form = StreamForm(obj=stream)
        form.populate_obj(stream)
        if form.validate_on_submit():
            db.session.add(stream)
            return {
                'msg': 'Stream updated.',
                'stream': stream.to_json(),
            }
        return {
            'msg': 'Validation failed.',
            'errors': form.errors,
        }, 400

    def delete(self, stream_id):
        """ Delete the stream with the given ID. """
        stream = Stream.query.get_or_404(stream_id)
        db.session.delete(stream)
        return {'msg': 'Stream deleted.'}
