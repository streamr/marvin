"""
    marvin.views.entries
    ~~~~~~~~~~~~~~~~~~~~

    CRUD endpoints for stream entries.

"""
# pylint: disable=no-self-use

from .. import db
from ..models import Entry, EntryForm

from flask.ext.restful import Resource

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

    def post(self):
        """ Create new entry. """
        form = EntryForm()
        if form.validate_on_submit():
            entry = Entry()
            form.populate_obj(entry)
            db.session.add(entry)
            return {'msg': 'Entry created.'}, 201
        return {
            'msg': 'Some attributes did not pass validation.',
            'errors': form.errors,
        }, 400
