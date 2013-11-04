"""
    marvin.views.stats
    ~~~~~~~~~~~~~~~~~~

    Show some key numbers about the current marvin database.

"""
from ..models import Movie, Stream, Entry

from flask import Blueprint, render_template

mod = Blueprint(__name__, 'marvin.stats')

@mod.route('/')
def stats_main():
    """ Show some key numbers. """
    stats = {
        'Number of movies': Movie.query.count(),
        'Number of streams': Stream.query.count(),
        'Number of entries': Entry.query.count(),
    }
    return render_template('stats.html', stats=stats)
