"""
    marvin.views.streams
    ~~~~~~~~~~~~~~~~~~~~

    CRUD endpoints for streams.

"""
# pylint: disable=no-self-use

from .. import db
from ..models import Stream, StreamForm, Entry

from flask import request
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
            'msg': 'Some attributes did not pass validation.',
            'errors': form.errors,
        }, 400


    def delete(self, stream_id):
        """ Delete the stream with the given ID. """
        stream = Stream.query.get_or_404(stream_id)
        db.session.delete(stream)
        return {'msg': 'Stream deleted.'}


class AllStreamView(Resource):
    """ C interface for streams. """

    def post(self):
        """ Create new stream. """
        form = StreamForm()
        if form.validate_on_submit():
            stream = Stream()
            form.populate_obj(stream)
            db.session.add(stream)
            db.session.commit()
            return {
                'msg': 'Stream created',
                'stream': stream.to_json(),
            }, 201
        return {
            'msg': 'Data did not validate.',
            'errors': form.errors,
        }, 400


class StreamEntrySearch(Resource):
    """ Read endpoint for entries in a stream. """

    def get(self, stream_id):
        """ Get entries for the given stream.

        Respect the following request parameters:

        * ``limit``: Restrict number of entries returned to this amount.
        * ``starttime_gt``: Only return entries that enter after this time, in ms.
        """
        max_number_of_entries = request.args.get('limit', 100)
        starttime_gt = request.args.get('starttime_gt', -1)
        entries = Stream.query.get_or_404(stream_id).entries.\
            filter(Entry.entry_point_in_ms > starttime_gt).\
            order_by(Entry.entry_point_in_ms.asc()).\
            limit(max_number_of_entries)
        return {
            'entries': [entry.to_json() for entry in entries],
        }
