"""
    marvin.views.entries
    ~~~~~~~~~~~~~~~~~~~~

    CRUD endpoints for stream entries.

"""
# pylint: disable=no-self-use

from .. import db
from ..models import Entry, EntryForm, Stream
from ..permissions import login_required

from flask.ext.restful import Resource
from flask.ext.principal import Permission, UserNeed

class EntryDetailView(Resource):
    """ RUD interface to entries. """

    def get(self, entry_id):
        """ Get the entry with the given ID. """
        entry = Entry.query.get(entry_id)
        return {
            'entry': entry.to_json(),
        }


    def put(self, entry_id):
        """ Update the entry with the given ID. """
        entry = Entry.query.get_or_404(entry_id)
        form = EntryForm(obj=entry)
        if form.validate_on_submit():
            form.populate_obj(entry)
            db.session.add(entry)
            return {
                'msg': 'Entry updated.',
                'entry': entry.to_json(),
            }
        return {
            'msg': 'Some attributes did not pass validation.',
            'errors': form.errors,
        }, 400


    def delete(self, entry_id):
        """ Delete the entry with the given ID. """
        entry = Entry.query.get(entry_id)
        db.session.delete(entry)
        return {'msg': 'Entry deleted.'}


class CreateEntryView(Resource):
    """ Create interface to entries. """

    @login_required
    def post(self, stream_id):
        """ Create new entry. """
        stream = Stream.query.get_or_404(stream_id)
        add_entry_to_stream_permission = Permission(UserNeed(stream.creator_id))
        if add_entry_to_stream_permission.can():
            form = EntryForm()
            if form.validate_on_submit():
                entry = Entry()
                form.populate_obj(entry)
                entry.stream = stream
                db.session.add(entry)
                db.session.commit()
                return {
                    'msg': 'Entry created.',
                    'entry': entry.to_json(),
                }, 201
            return {
                'msg': 'Some attributes did not pass validation.',
                'errors': form.errors,
            }, 400
        else:
            return {
                'msg': 'Only the creator can add entries to streams',
            }, 403
