from marvin.tests import fixtures
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
        fixtures.load(self.app, fixtures.COMPLETE)


    def test_correct_stats(self):
        with rendered_context(self.app) as context:
            response = self.client.get('/')
            stats = context['stats']

        self.assert200(response, mimetype='text/html; charset=utf-8')
        self.assertEqual(stats['Number of movies'], 2)
        self.assertEqual(stats['Number of streams'], 3)
        self.assertEqual(stats['Number of entries'], 9)
        self.assertEqual(stats['Number of users'], 2)
