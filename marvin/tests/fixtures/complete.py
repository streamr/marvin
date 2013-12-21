"""
    marvin.tests.fixtures.complete
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A fixture with data loaded in all models.

    Contains:

        * 2 movies (Avatar and Battleship)
        * 3 streams (Sins for both, Actors Introduced for Avatar)
        * 9 stream entries, evenly distributed among the streams

"""

from marvin.models import Movie, Stream, Entry, User

################### USERS

bob = User(
    username='bob',
    email='bob@example.com',
    password_hash='scrypt$1024:8:1$supersalt$supersecretpw',
)

alice = User(
    username='alice',
    email='alice@otherexample.com',
    password_hash='scrypt:1024:8:1$NaCl$topsecr3t',
)

################### MOVIES

avatar = Movie(
    title='Avatar',
    external_id='imdb:tt0499549',
    number_of_streams=2,
)

battleship = Movie(
    title='Battleship',
    external_id='imdb:tt1440129',
    number_of_streams=1,
)

################### STREAMS

avatar_sins = Stream(
    name='CinemaSins',
    movie=avatar,
    creator=bob,
)

avatar_actors = Stream(
    name='Actors Introduced',
    movie=avatar,
    creator=bob,
)

battleship_sins = Stream(
    name='CinemaSins',
    movie=battleship,
    creator=bob,
)

################### ENTRIES

avatar_fail_intro = Entry(
    entry_point_in_ms=5*60*1000,
    title='<h1>Title</h1>',
    content_type='text',
    content='{"text": "Massive TVs!"}',
    stream=avatar_sins,
)

avatar_fail_middle = Entry(
    entry_point_in_ms=45*60*1000,
    title='<h1>Title</h1>',
    content_type='text',
    content='{"text":"Trees without oxygen?"}',
    stream=avatar_sins,
)

avatar_fail_end = Entry(
    entry_point_in_ms=90*60*1000,
    title='<h1>Title</h1>',
    content_type='text',
    content='{"text":"Oral flower sex"}',
    stream=avatar_sins,
)

avatar_actor_sam = Entry(
    entry_point_in_ms=1*60*1000,
    title='<h1>Title</h1>',
    content_type='text',
    content='{"text":"Sam Worthington, Clash of the Titans, Terminator Salvation"}',
    stream=avatar_actors,
)

avatar_actor_sigourney = Entry(
    entry_point_in_ms=3*60*1000,
    title='<h1>Title</h1>',
    content_type='text',
    content='{"text":"Sigourney Weaver, Alien, Aliens, Ghostbusters"}',
    stream=avatar_actors,
)

battleship_sin_intro = Entry(
    entry_point_in_ms=20*1000,
    title='<h1>Title</h1>',
    content_type='text',
    content='{"text":"Hasbro films"}',
    stream=battleship_sins,
)

battleship_sin_early_intro = Entry(
    entry_point_in_ms=60*1000,
    title='<h1>Title</h1>',
    content_type='text',
    content='{"text":"Believes in wishes"}',
    stream=battleship_sins,
)

battleship_sin_middle = Entry(
    entry_point_in_ms=5*60*1000,
    title='<h1>Title</h1>',
    content_type='text',
    content='{"text":"No skype lag"}',
    stream=battleship_sins,
)

battleship_sin_outro = Entry(
    entry_point_in_ms=90*60*1000,
    title='<h1>Title</h1>',
    content_type='text',
    content='{"text":"No one says \\"You sunk my battleship\\""}',
    stream=battleship_sins,
)
