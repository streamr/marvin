External API
============

This document describes the public-facing API of marvin.

For endpoints where it's specified that authorization is required, a HTTP Authorization header is expected,
with type 'Token', like this: `Authorization: Token <auth_token>`. See details under the Users section for
how to obtain an auth_token.


Movies
------

A :class:`Movie <marvin.models.Movie>` is an entity to which streams are bound. Movies are found at the following
endpoints:

* ``GET /movies``: A list of movies in the marvin database, truncated to 15 results. This endpoints respect the
  following GET parameters:

    * `q`: A search query to limit movies by. Searches titles only.

  Each movie is an object with at least the following properties:

    * `href`: The URI for this movie. Use this for all operations on the movie, such as DELETE, PUT or GET.
    * :attr:`title <marvin.models.Movie.title>`
    * `_links`: An object with other relevant endpoints for the movie. Currently this includes:

        * `createStreams`: Where you should POST new streams. See under streams for the required attributes.

* ``GET /movies/<id>``: Get details for a single movie. Properties are subject to change, but you can expect *at least*
  the following:

    * `href`: URI of the movie.
    * :attr:`title <marvin.models.Movie.title>`
    * :attr:`streams <marvin.models.Movie.streams>`: A list of stream objects with at least an `href` and a
      :attr:`name <marvin.models.Stream.name>` attribute.


Streams
-------

A :class:`Stream <marvin.models.Stream>` is a collection of timecoded events that should occur during playback of a
movie. Streams are available at the following endpoints:

* ``GET /streams/<id>``: Details about the stream with the given ID. Properties include at least:

    * `href`: Link to this stream for further operations
    * :attr:`name <marvin.models.Stream.name>`
    * `_links`: Links for further operations with the stream. Currently includes the following keys:

        * `createEntry`: Create a new entry for this stream. See required properties under entries.
        * `entries`: An endpoint for querying for entries in this stream

* ``PUT /streams/<id>``: Update the given stream. All properties of the object must be present, anything missing will
  be deleted. Authorized user required, and only available to the user that created the stream.

* ``DELETE /streams/<id>``: Delete the given stream. Authorized user required, and only available to the user that
  created the stream.

* ``POST /movies/<movie_id>/createStream``: Create a new stream. Authorized user required. Required attributes:

    * :attr:`name <marvin.models.Stream.name>`


Entries
-------

An :class:`Entry <marvin.models.Entry>` is an event that occurs at some time during playback of a stream.

* ``GET /entries/<id>``: Get the details of a single entry.

* ``PUT /entries/<id>``: Edit the given entry. Access restricted to the user that created the stream.

* ``DELETE /entries/<id>``: Delete the given entry. Only available to stream owner.

* ``POST /streams/<stream_id>/createEntry``: Create a new entry. Required attributes:

    * :attr:`entry_point_in_ms <marvin.models.Entry.entry_point_in_ms>`
    * :attr:`title <marvin.models.Entry.title>`

* ``GET /streams/<id>/entries``: Get the Entries associated with this stream, sorted by time of appearance. This
  endpoint accepts the following parameter:

  * ``limit``: Limit the number of entries returned to this number. It's recommended to use this parameter to
    avoid eating up all the memory of a device, and rather ask for more later.
  * ``starttime_gt``: Only fetch entries starting later than this time, in `ms`. Since this is a strict greater then,
    you can pass in the starttime of the last entry you have, to fetch the next ones after that.


Users
-----

These endpoints are for creating users and getting auth tokens.

* ``POST /users``: Create a new user. Required fields:

    * ``username``: The desired username
    * ``password``: Desired password. Must be between 6 and 1024 characters long.
    * ``email``: The email the user wants to use to recover the account.

* ``GET /users/<user_id>``: View details for the given user. Access is restricted to logged in users, and users only
  have access to their own data.

* ``POST /login``: Get a new auth_token for user. Required fields:

    * ``identifier``: Either username or email of the user
    * ``password``: The user's password
