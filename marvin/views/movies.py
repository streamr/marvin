"""
    marvin.views.movies
    ~~~~~~~~~~~~~~~~~~~

    Endpoints related to movies.

"""
# pylint: disable=no-self-use

from .. import db
from ..models import Movie, MovieForm

from flask.ext.restful import Resource

class MovieView(Resource):
    """ RD interface to movies. """

    def get(self, movie_id):
        """ Get the movie with the given ID. """
        movie = Movie.query.get_or_404(movie_id)
        return {
            'movie': movie.to_json(),
        }


    def delete(self, movie_id):
        """ Delete the movie with the given ID. """
        movie = Movie.query.get_or_404(movie_id)
        db.session.delete(movie)
        return {'msg': 'Movie deleted.'}


class AllMoviesView(Resource):
    """ CR interface to all movies. """

    def post(self):
        """ Create new movie. """
        form = MovieForm()
        if form.validate_on_submit():
            movie = Movie()
            form.populate_obj(movie)
            db.session.add(movie)
            db.session.commit()
            return {
                'msg': 'Movie created',
                'movie': movie.to_json(),
                }, 201
        return {'msg': 'Data did not validate.', 'errors': form.errors}, 400


    def get(self):
        """ Get a list of id -> movie title pairs of all movies registered. """
        movies = Movie.query.all()
        return {'movies': [{movie.id: movie.title} for movie in movies]}
