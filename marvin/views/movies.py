"""
    marvin.views.movies
    ~~~~~~~~~~~~~~~~~~~

    Endpoints related to movies.

"""
# pylint: disable=no-self-use

from ..models import Movie

from flask import request
from flask.ext.restful import Resource
from logging import getLogger

_logger = getLogger('marvin.views.movies')


class MovieDetailView(Resource):
    """ Read interface to movies. """

    def get(self, movie_id):
        """ Get the movie with the given ID. """
        movie = Movie.query.get_or_404(movie_id)
        return {
            'movie': movie.to_json(),
        }


class AllMoviesView(Resource):
    """ R interface to all movies.

    Creation is in general not done manually by users, but rather automatically through search
    results and the likes. Only case where you can explicitly create a movie is by entering a url,
    so that we can look up the necessary parameters ourselves. This will be implemented later.
    """


    def get(self):
        """ Get a list of id -> movie title pairs of all movies registered. """
        # Import the task here since it will cause circular imports if it's done on the top
        from marvin.tasks import external_search

        search_query = request.args.get('q')
        limit = 15

        # Return results from our own db
        if search_query:
            search_words = search_query.split()
            final_search_query = '%'.join(search_words)
            movie_query = (Movie.query
                .filter(Movie.title.ilike('%' + final_search_query + '%'))
                .order_by(Movie.relevancy.desc())
                .limit(limit))
            _logger.info("Got search query for '%s'", search_query)
            movies = movie_query.all()
            if movies:
                _logger.info("Query for '%s' returned %d results", search_query, len(movies))
                # Good, we found something, return that, and look for more asynchronously
                external_search.delay(search_query)
            else:
                # Crap, database is empty, let's look for some more stuff synchronously, so that we don't
                # give any empty responses
                _logger.info("No movies found locally for query '%s', searching external resources...", search_query)
                external_search(search_query)
                movies = movie_query.all()
                _logger.info("Synchronous search for '%s' resulted in %d new movies", search_query, len(movies))
        else:
            movies = (Movie.query
                .filter(Movie.number_of_streams >= 1)
                .order_by(Movie.relevancy.desc())
                .limit(limit)
                .all())

        return {
            'movies': [movie.to_json(include_streams=False) for movie in movies],
        }
