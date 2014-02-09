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

from celery import chord
from logging import getLogger
import functools
import requests
import textwrap

_logger = getLogger('marvin.tasks')

celery = make_celery() # pylint: disable=invalid-name
task = functools.partial(celery.task, base=celery.Task)


@task(name='external-search')
def external_search(query):
    """ Query external resources like OMDb for a search term, and store the results
    locally.
    """
    omdb = OMDBFetcher()
    omdb.search_and_store(query)


@task(name='find-details')
def find_cover_art(external_ids=None):
    """ Look up cover art for all movies where it's missing. """
    if external_ids is None:
        movies = Movie.query.filter(Movie.cover_img == None).all()
    else:
        movies = Movie.query.filter(Movie.external_id.in_(external_ids)).all()
    for movie in movies:
        find_cover_art_for_movie.delay(movie.external_id)


@task(name='find-image-for-movie')
def find_cover_art_for_movie(external_id):
    """ Find cover art for one movie. """
    cover_art = get_omdb_property(external_id, 'Poster')
    if cover_art:
        save_new_property_on_movie(external_id, 'cover_img', cover_art)


@task(name='find-durations')
def find_durations(external_ids=None):
    """ Look up duration for movies where the data is missing, or for the given `external_ids`. """
    if external_ids is None:
        movies = Movie.query.filter(Movie.duration_in_s == None).all()
    else:
        movies = Movie.query.filter(Movie.external_id.in_(external_ids)).all()
    for movie in movies:
        find_duration_for_movie.delay(movie.external_id)


@task(name='find-duration-for-movie')
def find_duration_for_movie(external_id):
    """ Find the duration (in s) for one movie. """
    runtime = get_omdb_property(external_id, 'Runtime')
    if runtime:
        duration_in_s = parse_runtime_to_seconds(runtime)
        save_new_property_on_movie(external_id, 'duration_in_s', duration_in_s)


def parse_runtime_to_seconds(runtime):
    """ Parses number of seconds from a runtime string. """
    if 'min' in runtime:
        # Format is '123 min', f. ex.
        duration_in_s = int(runtime.rstrip(' min')) * 60
    elif ' h ' in runtime:
        # Format is '1 h 43' something
        hours, minutes = runtime.split(' h ', 1)
        minutes = int(hours)*60 + int(minutes)
        duration_in_s = minutes * 60
    else:
        _logger.error("Unknown runtime format found: '%s'", runtime)
        return 0
    return duration_in_s


@task(name='find-rating-parameters')
def find_rating_parameters(external_ids=None):
    """ Get metascore, imdb_rating and number_of_imdb_votes for movies. """
    update_relevancy_task = update_relevancy.s(ids=external_ids)
    get_meta = [
        find_imdb_ratings.s(external_ids),
        find_metacritic_ratings.s(external_ids),
    ]
    chord(get_meta)(update_relevancy_task)


@task(name='update-relevancy')
def update_relevancy(*args, **kwargs):
    if not kwargs.get('ids'):
        movies = Movie.query.all()
    else:
        movies = Movie.query.filter(Movie.external_id.in_(kwargs.get('ids'))).all()
    for movie in movies:
        update_relevancy_for_movie.delay(movie.external_id)


@task(name='update-relevancy-for-movie')
def update_relevancy_for_movie(external_id):
    movie = Movie.query.filter(Movie.external_id == external_id).one()
    _logger.info('Calculating new relevance for movie %s', movie.title)
    movie.update_relevancy()
    db.session.commit()


@task(name='find-imdb-ratings')
def find_imdb_ratings(external_ids):
    if external_ids is None:
        movies = Movie.query.filter(Movie.imdb_rating == 0).all()
    else:
        movies = Movie.query.filter(Movie.external_id.in_(external_ids)).all()
    for movie in movies:
        find_imdb_ratings_for_movie.delay(movie.external_id)


@task(name='find-imdb-ratings-for-movie')
def find_imdb_ratings_for_movie(external_id):
    provider, movie_id = external_id.split(':', 1)
    if provider != 'imdb':
        _logger.info("Can't poll OMDb for non-imdb sources")
        return
    obj = get_omdb_object(movie_id)
    if obj:
        rating_raw = obj.get('imdbRating', 'N/A')
        if rating_raw and rating_raw != 'N/A':
            rating = float(rating_raw)
            save_new_property_on_movie(external_id, 'imdb_rating', rating)
        number_of_votes_raw = obj.get('imdbVotes', 'N/A')
        if number_of_votes_raw and number_of_votes_raw != 'N/A':
            number_of_votes = int(number_of_votes_raw.replace(',', ''))
            save_new_property_on_movie(external_id, 'number_of_imdb_votes', number_of_votes)


@task(name='find-metacritic-ratings')
def find_metacritic_ratings(external_ids=None):
    """ Find the metascore for the given ids, or for movies without the field. """
    if external_ids is None:
        movies = Movie.query.filter(Movie.metascore == 0).all()
    else:
        movies = Movie.query.filter(Movie.external_id.in_(external_ids)).all()
    for movie in movies:
        find_metacritic_rating_for_movie.delay(movie.external_id)


@task(name='find-metacritic-rating-for-movie')
def find_metacritic_rating_for_movie(external_id):
    """ Find metascore for a single movie. """
    metascore_raw = get_omdb_property(external_id, 'Metascore')
    if metascore_raw:
        metascore = int(metascore_raw)
        save_new_property_on_movie(external_id, 'metascore', metascore)


def get_omdb_property(external_id, property_name):
    """ Get the given property of an object from OMDb. Returns None if property is not found, or is N/A. """
    provider, movie_id = external_id.split(':', 1)
    if provider != 'imdb':
        _logger.info("Can't poll OMDb for non-imdb sources")
        return
    obj = get_omdb_object(movie_id)
    if obj:
        prop = obj.get(property_name)
        if prop and prop != 'N/A':
            _logger.info("Successfully OMDb query for '%s', found '%s'=%s", movie_id, property_name, prop)
            return prop
    _logger.info("OMDb query for property '%s' on '%s' resulted in no hits.", property_name, movie_id)
    return None


def save_new_property_on_movie(external_id, property_name, property):
    _logger.info("Saving property %s=%s to movie %s", property_name, property, external_id)
    movie = Movie.query.filter_by(external_id=external_id).one()
    setattr(movie, property_name, property)
    db.session.commit()


def get_omdb_object(imdb_id):
    """ Fetch the object with the given IMDb ID from OMDb. Returns None on failures. """
    _logger.info("Querying OMDb for movie with id '%s'..", imdb_id)
    query_params = {
        'i': imdb_id,
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
            find_cover_art.delay(new_movies)
            find_durations.delay(new_movies)
            find_rating_parameters.delay(new_movies)


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
