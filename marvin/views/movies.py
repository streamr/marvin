"""
    marvin.views.movies
    ~~~~~~~~~~~~~~~~~~~

    Endpoints related to movies.

"""
# pylint: disable=no-self-use

from .. import db
from ..models import Movie, MovieForm

from flask import request
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
        return {
            'msg': 'Data did not validate.',
            'errors': form.errors,
        }, 400


    def get(self):
        """ Get a list of id -> movie title pairs of all movies registered. """
        search_query = request.args.get('q')
        if search_query:
            movies = Movie.query.filter(Movie.title.like('%' + search_query + '%'))
        else:
            movies = Movie.query.all()
        return {
            'movies': [movie.to_json(include_streams=False) for movie in movies],
        }
