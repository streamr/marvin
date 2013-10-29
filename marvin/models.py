"""
    marvin.models
    ~~~~~~~~~~~~~

    Here we define the models we use in marvin. If this module grows too large,
    make it a package and split it up into smaller pieces.

"""
from . import db

from flask.ext.wtf import Form
from wtforms_alchemy import model_form_factory

ModelForm = model_form_factory(Form)

class Movie(db.Model):
    """ Movies are the first thing the user will search for.

    Through a movie the user can find streams related to this movie.
    Most metadata should be fetched automatically from IMDb/TMDB.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), index=True, nullable=False)

    def __init__(self, **kwargs):
        """ Create new movie object.

        :param kwargs: Set object properties directly from the constructor.
        """
        self.__dict__.update(kwargs)


    def to_json(self):
        """ A dict representation of the movie that can be used for serialization. """
        return {
            'id': self.id,
            'title': self.title,
        }


class MovieForm(ModelForm):
    """ The form used to validate new movie objects. """

    class Meta(object):
        model = Movie
