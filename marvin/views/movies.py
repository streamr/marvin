"""
    marvin.views.movies
    ~~~~~~~~~~~~~~~~~~~

    Endpoints related to movies.

"""
# pylint: disable=no-self-use

from .. import db
from ..models import Movie

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
    """ R interface to all movies.

    Creation is in general not done manually by users, but rather automatically through search
    results and the likes. Only case where you can explicitly create a movie is by entering a url,
    so that we can look up the necessary parameters ourselves. This will be implemented later.
    """

    # This should be implemented when we want users to be able to create movies **not** found on any
    # of the sites we scrape for information
    # def post(self):
    #     """ Create new movie. """
    #     form = MovieForm()
    #     if form.validate_on_submit():
    #         movie = Movie()
    #         form.populate_obj(movie)
    #         db.session.add(movie)
    #         db.session.commit()
    #         return {
    #             'msg': 'Movie created',
    #             'movie': movie.to_json(),
    #         }, 201
    #     return {
    #         'msg': 'Data did not validate.',
    #         'errors': form.errors,
    #     }, 400


    def get(self):
        """ Get a list of id -> movie title pairs of all movies registered. """
        # Import the task here since it will cause circular imports if it's done on the top
        from marvin.tasks import external_search

        search_query = request.args.get('q')

        # Trigger an external search for movies
        external_search.delay(search_query)

        # Return results from our own db
        if search_query:
            movies = Movie.query.filter(Movie.title.like('%' + search_query + '%'))
        else:
            movies = Movie.query.all()
        return {
            'movies': [movie.to_json(include_streams=False) for movie in movies],
        }
