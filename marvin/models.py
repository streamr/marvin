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
    #: Identifies the movie uniquely. Do not make assumptions about the nature of this field
    #: as it might change without notice. Is completely unrelated to other IDs found elsewhere
    #: for the same movie, like on IMDb or similar sites.
    id = db.Column(db.Integer, primary_key=True)
    #: The title of the movie. Note that this field is *not sufficient* to uniquely identify a
    #: movie. Always use IDs if you need to do that.
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
