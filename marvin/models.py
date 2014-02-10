"""
    marvin.models
    ~~~~~~~~~~~~~

    Here we define the models we use in marvin. If this module grows too large,
    make it a package and split it up into smaller pieces.

"""
from . import db
from .fields import JSONField
from .security import generate_pw_hash

from datetime import datetime
from flask import url_for, current_app
from flask.ext.wtf import Form
from itsdangerous import constant_time_compare, URLSafeSerializer
from sqlalchemy_defaults import Column
from sqlalchemy_utils import EmailType, JSONType
from time import time
from wtforms_alchemy import model_form_factory
from wtforms.fields import TextField
from wtforms.validators import Length


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
    #: Namespaced identification of some resource, like a movies ID om IMDb, or it's ID on
    #: YouTube/Vimeo, or just a URI if we don't know the site already. Format like "imdb:tt01"
    #: or "youtube:Fq00mCqBMY8".
    external_id = Column(db.String(200), unique=True, index=True)
    #: The title of the movie. Note that this field is *not sufficient* to uniquely identify a
    #: movie. Always use IDs if you need to do that.
    title = Column(db.String(100), index=True)
    #: What kind of movie is this? E.g. actual movie, episode, clip found on internet?
    category = Column(db.String(20), default='movie')
    #: Time added to database
    datetime_added = Column(db.DateTime, auto_now=True)
    #: Year the movies was first shown
    year = Column(db.Integer, min=1880, max=2050)
    #: Small cover art, 300px-ish
    cover_img = Column(db.String(100), nullable=True)
    #: An aggregate of number of streams available
    number_of_streams = Column(db.Integer, default=0, nullable=False, min=0)
    # Movie duration, in seconds
    duration_in_s = Column(db.Integer, min=0)
    # IMDb rating
    imdb_rating = Column(db.Float, default=0.0, max=10.0, min=0.0, nullable=False)
    # Number of votes on IMDb
    number_of_imdb_votes = Column(db.Integer, default=0, min=0, nullable=False)
    # Score from metacritic
    metascore = Column(db.Integer, default=0, min=0, max=100, nullable=False)
    # A measurement of how relevant this movie is, used for search ranking purposes
    relevancy = Column(db.Float, min=0.0, default=0, nullable=False)


    def __init__(self, **kwargs):
        """ Create new movie object.

        :param kwargs: Set object properties directly from the constructor.
        """
        self.__dict__.update(kwargs)


    def to_json(self, include_streams=True):
        """ A dict representation of the movie that can be used for serialization. """
        movie = {
            'href': url_for('moviedetailview', movie_id=self.id, _external=True),
            'external_id': self.external_id,
            'title': self.title,
            'category': self.category,
            'datetime_added': self.datetime_added,
            'year': self.year,
            'cover_img': self.cover_img,
            'number_of_streams': self.number_of_streams,
            'imdb_rating': self.imdb_rating,
            'imdb_votes': self.number_of_imdb_votes,
            'metascore': self.metascore,
            'duration_in_s': self.duration_in_s,
            '_links': {
                'createStream': url_for('createstreamview', movie_id=self.id, _external=True),
            },
        }
        if include_streams:
            movie['streams'] = [stream.to_json(include_movie=False) for stream in self.streams]
        return movie


    def update_relevancy(self):
        """ Calculate a new relevancy rating for the movie.

        The IMDb rating is weighted the most, contributing a potential 200 points out of a 325 max,
        while the metascore ranking can contribute another 100 points, 25 points for number of
        votes, and then the score is discounted by a factor of .99 for each year since it's relase.
        """
        imdb_ranking = 20*self.imdb_rating
        metascore_ranking = self.metascore
        imdb_votes_ranking = min(self.number_of_imdb_votes, 25000) / 1000
        current_year = datetime.now().year
        years_since_release = current_year - self.year
        age_discount = 0.99**(years_since_release)
        self.relevancy = (imdb_ranking + imdb_votes_ranking + metascore_ranking)*age_discount


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
    movie_id = Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    #: The movie this stream is associated to.
    movie = db.relationship('Movie', backref=db.backref('streams', lazy='dynamic'))
    #: Foreign key to the user that created the stream
    creator_id = Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #: The user that created the stream
    creator = db.relationship('User', backref=db.backref('created_streams', lazy='dynamic'))


    def __init__(self, movie=None, creator=None, **kwargs):
        """ Create new stream.

        :param movie: The movie this stream should be associated to.
        :param creator: The user that created the stream.
        :param kwargs: Set object properties from constructor.
        """
        self.movie = movie
        self.creator = creator
        self.__dict__.update(kwargs)


    def to_json(self, include_movie=True):
        """ Get a dict representation of the stream suitable for serialization. """
        stream = {
            'href': url_for('streamdetailview', stream_id=self.id, _external=True),
            'name': self.name,
            'author': {
                'username': self.creator.username,
                'href': url_for('userdetailview', user_id=self.creator.id, _external=True),
            },
            '_links': {
                'createEntry': url_for('createentryview', stream_id=self.id, _external=True),
                'entries': url_for('streamentrysearch', stream_id=self.id, _external=True),
            }
        }
        if include_movie:
            stream['movie'] = {
                'href': url_for('moviedetailview', movie_id=self.movie_id, _external=True),
                'title': self.movie.title,
            }
        return stream


class StreamForm(ModelForm):
    """ A form used to validate new streams. """

    class Meta(object):
        model = Stream
        # explicitly define which fields should be considered
        only = (
            'name',
        )


class Entry(db.Model):
    """ User-created content that appears at a given time in the movie. """
    __lazy_options__ = {}

    #: Unique identifier
    id = Column(db.Integer, primary_key=True)
    #: The time this entry should appear, in ms since the beginning of the stream
    entry_point_in_ms = Column(db.Integer, min=0, nullable=False)
    #: The title of the entry
    title = Column(db.String(30), nullable=False)
    #: The type of content, e.g. 'text', 'wiki', 'imdb:actor', etc.
    content_type = Column(db.String(20), nullable=False)
    #: The content of the entry, as a JSON data structure
    content = Column(JSONType,
        info={
            'form_field_class': JSONField,
            #'validators': JSONValidator(),
        },
    )
    #: Foreign key to a stream
    stream_id = Column(db.Integer,
        db.ForeignKey('stream.id'),
        nullable=False,
    )
    #: The stream this entry belongs to
    stream = db.relationship('Stream', backref=db.backref('entries', lazy='dynamic'))


    def __init__(self, stream=None, **kwargs):
        """ Create new entry.

        :param stream: The stream this entry should be associated to.
        :param kwargs: Properties of the stream that can be set from the constructor.
        """
        self.stream = stream
        self.__dict__.update(kwargs)


    def to_json(self):
        """ Get a dict representation of the entry suitable for serialization. """
        return {
            'href': url_for('entrydetailview', entry_id=self.id, _external=True),
            'entry_point_in_ms': self.entry_point_in_ms,
            'content_type': self.content_type,
            'content': self.content,
            'title': self.title,
            'stream': {
                'href': url_for('streamdetailview', stream_id=self.stream_id, _external=True),
                'name': self.stream.name,
            },
        }


class EntryForm(ModelForm):
    """ Form used to validate new entries. """

    class Meta(object):
        model = Entry
        # explicitly declare which fields to consider in the form
        only = (
            'entry_point_in_ms',
            'content_type',
            'content',
            'title',
        )


class User(db.Model):
    """ A user of the app. """
    __lazy_options__ = {}

    #: Unique identifier for this user
    id = Column(db.Integer, primary_key=True)
    #: The users chosen username
    username = Column(db.String(20), index=True, unique=True)
    #: The user's email address
    email = Column(EmailType, nullable=False, unique=True)
    #: A string in the format method$salt$hash, where method for now will be scrypt:N:p:r,
    #: with N, p and r can be chosen to be arbitrary strong on a given machine.
    password_hash = Column(db.String(250))
    #: Date and time of signup
    user_created_datetime = Column(db.DateTime, auto_now=True)


    def __init__(self, **kwargs):
        """ Create a new user.

        :param kwargs: All properties can be set directory from the constructor.
        """
        if 'password' in kwargs:
            password = kwargs.pop('password')
            self.password_hash = generate_pw_hash(password)
        self.__dict__.update(kwargs)


    def is_authenticated(self):
        """ Used to tell the difference between authenticated users and anonymous users. """
        # pylint: disable=no-self-use
        return True


    def to_json(self, include_personal_data=False):
        """ A dict representation of the user.

        :param include_personal_data: Whether to include sensitive data such as email.
        """
        data = {
            'username': self.username,
            'href': url_for('userdetailview', user_id=self.id),
            'streams': [{
                'href': url_for('streamdetailview', stream_id=s.id, _external=True),
                'name': s.name,
                } for s in self.created_streams],
        }

        if include_personal_data:
            data['email'] = self.email
            data['signup_date'] = self.user_created_datetime

        return data


    def get_auth_token(self):
        """ Get a auth token the user can use to authenticate agains the service. """
        # The data keys should be as short as possible to keep the token short
        data = {
            # The user's id
            'i': self.id,
            # Time of issue
            't': time(),
            # Last characters of user's hashed password, makes sure the key is automatically
            # expired if the user changes password
            'p': self.password_hash[-10:],
        }
        serializer = URLSafeSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps(data)


    def verify_auth_data(self, auth_data):
        """ Verify that an auth_data is valid for this user.

        In pracice this means checking that the password in the given data is still valid
        and has not expired yet.
        """
        return constant_time_compare(auth_data['p'].encode('ascii'), self.password_hash[-10:].encode('ascii'))


class AnonymousUser(object):
    """ Represents an anonymous user. """

    def is_authenticated(self):
        """ Used to tell anonymous users apart from authenticated users. Always returns False. """
        # pylint: disable=no-self-use
        return False


class UserForm(ModelForm):
    """ Form used to validate new user creation. """

    class Meta(object):
        model = User
        only = (
            'username',
            'email',
        )

    password = TextField(validators=[Length(min=6, max=1024)])


class UserLoginForm(Form):
    """ Form used to validate user logins. """

    identifier = TextField()
    password = TextField(validators=[Length(min=6, max=1024)])
