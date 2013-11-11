from marvin.models import Movie, Stream, Entry
from marvin.tests import TestCaseWithTempDB

from contextlib import contextmanager
from flask import template_rendered


@contextmanager
def rendered_context(app):
    """ Store templates and contexts rendered during a request.

    May be refactored out if needed elsewhere.
    """
    merged_context = {}
    def record(sender, template, context, **extra): # pylint: disable=unused-argument
        merged_context.update(context)
    template_rendered.connect(record, app)
    try:
        yield merged_context
    finally:
        template_rendered.disconnect(record, app)


class StatsViewTest(TestCaseWithTempDB):

    def setUp(self):

        # Add movies
        avatar = Movie(
            title='Avatar',
            external_id='imdb:tt0499549',
        )
        battleship = Movie(
            title='Battleship',
            external_id='imdb:tt1440129',
        )

        # Add streams
        avatar_sins = Stream(
            name='CinemaSins',
            movie=avatar,
        )
        avatar_actors = Stream(
            name='Actors Introduced',
            movie=avatar,
        )
        battleship_sins = Stream(
            name='CinemaSins',
            movie=battleship,
        )

        # Add entries
        avatar_fail_intro = Entry(
            entry_point_in_ms=5*60*1000,
            title='<h1>Title</h1>',
            content='Massive TVs!',
            stream=avatar_sins,
        )
        avatar_fail_middle = Entry(
            entry_point_in_ms=45*60*1000,
            title='<h1>Title</h1>',
            content='Trees without oxygen?',
            stream=avatar_sins,
        )
        avatar_fail_end = Entry(
            entry_point_in_ms=90*60*1000,
            title='<h1>Title</h1>',
            content='Oral flower sex',
            stream=avatar_sins,
        )

        avatar_actor_sam = Entry(
            entry_point_in_ms=1*60*1000,
            title='<h1>Title</h1>',
            content='Sam Worthington, Clash of the Titans, Terminator Salvation',
            stream=avatar_actors,
        )
        avatar_actor_sigourney = Entry(
            entry_point_in_ms=3*60*1000,
            title='<h1>Title</h1>',
            content='Sigourney Weaver, Alien, Aliens, Ghostbusters',
            stream=avatar_actors,
        )

        battleship_sin_intro = Entry(
            entry_point_in_ms=20*1000,
            title='<h1>Title</h1>',
            content='Hasbro films',
            stream=battleship_sins,
        )
        battleship_sin_early_intro = Entry(
            entry_point_in_ms=60*1000,
            title='<h1>Title</h1>',
            content='Believes in wishes',
            stream=battleship_sins,
        )
        battleship_sin_middle = Entry(
            entry_point_in_ms=5*60*1000,
            title='<h1>Title</h1>',
            content='No skype lag',
            stream=battleship_sins,
        )
        battleship_sin_outro = Entry(
            entry_point_in_ms=90*60*1000,
            title='<h1>Title</h1>',
            content='No one says "You sunk my battleship"',
            stream=battleship_sins,
        )

        self.addItems(
            avatar,
            battleship,
            avatar_sins,
            avatar_actors,
            battleship_sins,
            avatar_fail_intro,
            avatar_fail_middle,
            avatar_fail_end,
            avatar_actor_sam,
            avatar_actor_sigourney,
            battleship_sin_intro,
            battleship_sin_early_intro,
            battleship_sin_middle,
            battleship_sin_outro,
        )


    def test_correct_stats(self):
        with rendered_context(self.app) as context:
            response = self.client.get('/')
            stats = context['stats']

        self.assert200(response, mimetype='text/html; charset=utf-8')
        self.assertEqual(stats['Number of movies'], 2)
        self.assertEqual(stats['Number of streams'], 3)
        self.assertEqual(stats['Number of entries'], 9)
