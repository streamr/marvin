"""
    marvin.models
    ~~~~~~~~~~~~~

    Here we define the models we use in marvin. If this module grows too large,
    make it a package and split it up into smaller pieces.

"""
from . import db

from flask.ext.wtf import Form
from wtforms_alchemy import model_form_factory
from sqlalchemy_defaults import Column

ModelForm = model_form_factory(Form)

class Movie(db.Model):
    """ Movies are the first thing the user will search for.

    Through a movie the user can find streams related to this movie.
    Most metadata should be fetched automatically from IMDb/TMDB.
    """
    __lazy_options__ = {}

    #: Identifies the movie uniquely. Do not make assumptions about the nature of this field
    #: as it might change without notice. Is completely unrelated to other IDs found elsewhere
    #: for the same movie, like on IMDb or similar sites.
    id = Column(db.Integer, primary_key=True)
    #: The title of the movie. Note that this field is *not sufficient* to uniquely identify a
    #: movie. Always use IDs if you need to do that.
    title = Column(db.String(100), index=True)


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
            'streams': [{
                'id': stream.id,
                'name': stream.name,
                } for stream in self.streams],
        }


class MovieForm(ModelForm):
    """ The form used to validate new movie objects. """

    class Meta(object):
        model = Movie


class Stream(db.Model):
    """ A collection of related, timecoded entries that accompanies a movie.

    Entries in a stream will usually have some common theme, like annoucing new
    actors that enter the screen, or providing references for topics mentioned
    in a movie.
    """
    __lazy_options__ = {}

    #: Unique identifier for this stream. Do not make assumptions about it's format, subject to change.
    id = Column(db.Integer, primary_key=True)
    #: A user chosen name for the stream. Users can change this at their own discretion, do not assume to
    #: be constant.
    name = Column(db.String(30), nullable=False)
    #: Foreign key to a movie
    movie_id = Column(db.Integer, db.ForeignKey('movie.id'))
    #: The movie this stream is associated to.
    movie = db.relationship('Movie', backref=db.backref('streams', lazy='dynamic'))


    def __init__(self, movie=None, **kwargs):
        """ Create new stream.

        :param movie: The movie this stream should be associated to.
        :param kwargs: Set object properties from constructor.
        """
        self.movie = movie
        self.__dict__.update(kwargs)


    def to_json(self):
        """ Get a dict representation of the stream suitable for serialization. """
        return {
            'id': self.id,
            'name': self.name,
            'movie': {
                'id': self.movie_id,
                'title': self.movie.title,
            }
        }


class StreamForm(ModelForm):
    """ A form used to validate new streams. """

    class Meta(object):
        model = Stream
