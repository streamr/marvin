External API
============

This document describes the public-facing API of marvin. For now, there's no authentication required to use the API,
but this is likely to change.


Movies
------

A :class:`Movie <marvin.models.Movie>` is an entity to which streams are bound. Movies are found at the following endpoints:

* ``GET /movies``: A list of all movies in the marvin database. Each movie is am object with at least an
  :attr:`id <marvin.models.Movie.id>` and a :attr:`title <marvin.models.Movie.title>`.

* ``POST /movies``: Create a new movie. Required attributes:

    * :attr:`title <marvin.models.Movie.title>`

* ``GET /movies/<id>``: Get details for a single movie. Properties are subject to change, but you can expect *at least*
   the following:
    * :attr:`id <marvin.models.Movie.id>`
    * :attr:`title <marvin.models.Movie.title>`
    * :attr:`streams <marvin.models.Movie.streams>`: A list of stream objects with at least an
      :attr:`id <marvin.models.Stream.id>` and a :attr:`name <marvin.models.Stream.name>` attribute.

* ``DELETE /movies/<id>``: Delete the movie with the given id.


Streams
-------

A :class:`Stream <marvin.models.Stream>` is a collection of timecoded events that should occur during playback of a movie. Streams are available at the
following endpoints:

* ``GET /streams/<id>``: Details about the stream with the given ID. Properties include at least
  :attr:`id <marvin.models.Stream.id>` and :attr:`name <marvin.models.Stream.name>`.

* ``POST /streams``: Create a new stream. Required attributes:

    * :attr:`name <marvin.models.Stream.name>`
    * :attr:`movie_id <marvin.models.Stream.movie_id>`
