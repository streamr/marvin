"""
    marvin.tasks
    ~~~~~~~~~~~~

    Asynchronous tasks that might be spawned by the webserver for later
    processeing. Put everything that's too slow to be executed directly
    by the webserver here.

"""
# pylint: disable=no-self-use

from . import db, make_celery
from .models import Movie

from logging import getLogger

import requests
import textwrap

_logger = getLogger('marvin.tasks')

celery = make_celery() # pylint: disable=invalid-name

@celery.task(name='external-search', base=celery.Task)
def external_search(query):
    """ Query external resources like OMDb for a search term, and store the results
    locally.
    """
    omdb = OMDBFetcher()
    omdb.search_and_store(query)


@celery.task(name='find-images', base=celery.Task)
def find_cover_art(external_ids=None):
    """ Look up images for all movies where it's missing. """
    if external_ids is None:
        movies = Movie.query.filter(Movie.cover_img == None).all()
    else:
        movies = Movie.query.filter(Movie.external_id.in_(external_ids)).all()
    for movie in movies:
        find_cover_art_for_movie.delay(movie.external_id)


@celery.task(name='find-image-for-movie', base=celery.Task)
def find_cover_art_for_movie(external_id):
    """ Find cover art for one movie. """
    _logger.info("Searching for cover art for %s...", external_id)
    provider, movie_id = external_id.split(':', 1)
    if provider == 'imdb':
        query_params = {
            'i': movie_id,
        }
        response = requests.get('http://omdbapi.com', params=query_params)
        if response.status_code != 200:
            _logger.error(textwrap.dedent("""OMDb query for movie details returned non-200 status code.
                URL:         %s
                Status code: %d
                Response:    %s
            """), response.url, response.status_code, response.text)
            return
        json_results = response.json()
        cover_art = json_results.get('Poster')
        if cover_art and cover_art != 'N/A':
            movie = Movie.query.filter_by(external_id=external_id).one()
            _logger.info("Cover art for %s (%s) found", external_id, movie.title)
            movie.cover_img = cover_art
            db.session.add(movie)
            db.session.commit()
    else:
        _logger.warning("I don't know how to find cover images for provider '%s'", provider)


class OMDBFetcher(object):
    """
        Query OMDb for movies, store to our db. OMDb provides an imdb ID for all
        entities, so everything saved from this fetcher will be with a imdb: external_id.
    """

    OMDB_URL = 'http://www.omdbapi.com/'

    def search_and_store(self, query):
        """ Get OMDb search results for `query`, store the results.

        :param query: The query to search for. Queryies shorter than 2 characters will be ignored.
        """
        # OMDb refuses queries shorter than 2 chars
        if len(query) > 1:
            results = self._query_omdb(query)
            new_movies = self._parse_omdb_results(results)
            find_cover_art.delay(new_movies)


    def _query_omdb(self, query):
        _logger.info("Querying OMDB for '%s'", query)
        payload = {'s': query}
        results = requests.get(self.OMDB_URL, params=payload)
        if results.status_code != 200:
            _logger.error(textwrap.dedent("""OMDb request returned non-200 status code.
                Status code: %d
                Query:       %s
                Response:    %s
            """), results.status_code, results.url, results.text)
        try:
            json_results = results.json()
            return json_results
        except requests.exceptions.RequestException as ex: # pragma: no cover
            _logger.warning(textwrap.dedent("""JSON decoding of OMDB response failed. Details:
                Status code: %d
                URL:         %s
                Payload:     %s
                Exception:   %s
            """), results.status_code, results.url, results.text, ex)


    def _parse_omdb_results(self, results):
        external_ids = ['imdb:%s' % omdb_movie['imdbID'] for omdb_movie in results.get('Search', [])]
        existing_movies = Movie.query.filter(Movie.external_id.in_(external_ids))
        new_ids = external_ids[:]
        for existing_movie in existing_movies:
            new_ids.remove(existing_movie.external_id)
        accepted_types = ['movie', 'episode']
        for omdb_movie in results.get('Search', []):
            if omdb_movie['Type'] in accepted_types and 'imdb:%s' % omdb_movie['imdbID'] in new_ids:
                movie = Movie()
                movie.title = omdb_movie['Title']
                movie.category = omdb_movie['Type']
                movie.year = int(omdb_movie['Year'])
                movie.external_id = 'imdb:%s' % omdb_movie['imdbID']
                db.session.add(movie)
                _logger.info("New movie added: '%s' (%d)", movie.title, movie.year)
        db.session.commit()
        return new_ids
