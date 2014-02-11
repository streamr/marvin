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

from collections import namedtuple
from logging import getLogger
import functools
import re
import requests
import textwrap

_logger = getLogger('marvin.tasks')

celery = make_celery() # pylint: disable=invalid-name
task = functools.partial(celery.task, base=celery.Task, ignore_result=True) # pylint: disable=invalid-name


@task(name='external-search')
def external_search(query):
    """ Query external resources like OMDb for a search term, and store the results
    locally.
    """
    omdb = OMDBFetcher()
    omdb.search_and_store(query)


@task(name='update-meta')
def update_meta(external_ids=None):
    """ Update the metadata from OMDb for the given IDs, or for all movies if not defined. """
    if external_ids is None:
        movies = Movie.query.all()
    else:
        movies = Movie.query.filter(Movie.external_id.in_(external_ids)).all()
    for movie in movies:
        update_meta_for_movie.delay(movie.external_id)


@task(name='update-meta-for-movie')
def update_meta_for_movie(external_id):
    """ Update metadata for a given movie.

    Fields updated include cover image, runtime, IMDb rating and number of votes and the metascore.
    """
    omdb = get_omdb_object(external_id)
    movie = Movie.query.filter(Movie.external_id == external_id).one()
    Mapper = namedtuple('Mapper', ['omdb_property', 'movie_property', 'parser']) # pylint: disable=invalid-name
    mappers = [
        Mapper('Poster', 'cover_img', str),
        Mapper('Runtime', 'duration_in_s', parse_runtime_to_seconds),
        Mapper('Metascore', 'metascore', int),
        Mapper('imdbRating', 'imdb_rating', float),
        Mapper('imdbVotes', 'number_of_imdb_votes', lambda s: int(s.replace(',', '')))
    ]
    for mapper in mappers:
        save_omdb_property_to_movie(movie, omdb, mapper)
    _logger.info("Updating relevancy for movie '%s'", movie.title)
    movie.update_relevancy()
    db.session.commit()


def save_omdb_property_to_movie(movie, omdb_results, mapper):
    """ Extract a value from the omdb results and save it to the movie. """
    prop_raw = omdb_results.get(mapper.omdb_property, 'N/A')
    if prop_raw != 'N/A':
        prop = mapper.parser(prop_raw)
        setattr(movie, mapper.movie_property, prop)


def parse_runtime_to_seconds(runtime):
    """ Parses number of seconds from a runtime string. """
    first_match = re.match(r'^[\d]{1,3} min$', runtime)
    if first_match:
        # Format is '123 min'
        duration_in_s = int(runtime.rstrip(' min')) * 60
        return duration_in_s

    second_match = re.match(r'^(\d) h ([\d]{1,2}) min$', runtime)
    if second_match:
        # Format is '1 h 43 min'
        hours, minutes = second_match.groups()
        minutes = int(hours)*60 + int(minutes)
        duration_in_s = minutes * 60
        return duration_in_s

    third_match = re.match(r'^(\d) h$', runtime)
    if third_match:
        # Format is '1 h'
        hours = int(runtime.split(' h', 1)[0])
        duration_in_s = hours * 3600
        return duration_in_s

    _logger.error("Unknown runtime format found: '%s'", runtime)
    return 0


def get_omdb_object(external_id):
    """ Fetch the object with the given IMDb ID from OMDb. Returns None on failures. """
    provider, movie_id = external_id.split(':', 1)
    if provider != 'imdb':
        _logger.info("Can't poll OMDb for non-imdb sources")
        return
    _logger.info("Querying OMDb for movie with id '%s'..", movie_id)
    query_params = {
        'i': movie_id,
    }
    return omdb_request(query_params)


def omdb_request(payload):
    """ A proxy around OMDb with error handling. """
    response = requests.get('http://omdbapi.com', params=payload)
    if response.status_code != 200:
        _logger.error(textwrap.dedent("""OMDb query for movie details returned non-200 status code.
            URL:         %s
            Status code: %d
            Response:    %s
        """), response.url, response.status_code, response.text)
        return None
    json_results = response.json()
    return json_results


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
            results = self._search_omdb(query)
            new_movies = self._parse_omdb_results(results)
            if new_movies:
                update_meta.delay(new_movies)


    def _search_omdb(self, query):
        _logger.info("Searching OMDB for '%s'", query)
        payload = {'s': query}
        return omdb_request(payload)


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
