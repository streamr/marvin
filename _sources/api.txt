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

* ``PUT /streams/<id>``: Update the given stream. All properties of the object must be present, anything missing will be deleted.

* ``DELETE /streams/<id>``: Delete the given stream.

* ``POST /streams``: Create a new stream. Required attributes:

    * :attr:`name <marvin.models.Stream.name>`
    * :attr:`movie_id <marvin.models.Stream.movie_id>`


Entries
-------

An :class:`Entry <marvin.models.Entry>` is an event that occurs at some time during playback of a stream.

* ``GET /entries/<id>``: Get the details of a single entry.

* ``PUT /entries/<id>``: Edit the given entry.

* ``DELETE /entries/<id>``: Delete the given entry.

* ``POST /entries``: Create a new entry. Required attributes:

    * :attr:`entry_point_in_ms <marvin.models.Entry.entry_point_in_ms>`
    * :attr:`stream_id <marvin.models.Entry.stream_id>`
    * :attr:`title <marvin.models.Entry.title>`

* ``GET /streams/<id>/entries``: Get the Entries associated with this stream, sorted by time of appearance. This
  endpoint accepts the following parameter:

  * ``limit``: Limit the number of entries returned to this number. It's recommended to use this parameter to
    avoid eating up all the memory of a device, and rather ask for more later.
  * ``starttime_gt``: Only fetch entries starting later than this time, in `ms`. Since this is a strict greater then,
    you can pass in the starttime of the last entry you have, to fetch the next ones after that.
