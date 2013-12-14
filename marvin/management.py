"""
    marvin.management
    ~~~~~~~~~~~~~~~~~

    Configures the manager, and acts as an entry point for the manage command.

"""
# pylint: disable=invalid-name
from . import create_app, db, init_db
from .models import Stream, Entry, Movie

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from os import path

app = create_app()
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

@manager.command
def runserver():
    """ Start a devserver on port 5000 """
    config_file = path.abspath(path.join(path.dirname(__file__), '..', 'dev_config.py'))
    dev_app = create_app(config_file=config_file)
    init_db(dev_app)
    dev_app.run()


@manager.command
def delete_streams_and_entries(wipe_movies=False):
    """ Delete all streams and entries.

    After deletion it will reset movie stream counts to 0. Can optionally also
    delete all movies, if the --wipe_movies flag is used. """

    all_streams = Stream.query.all()
    for stream in all_streams:
        db.session.delete(stream)
    all_entries = Entry.query.all()
    for entry in all_entries:
        db.session.delete(entry)

    if wipe_movies:
        all_movies = Movie.query.all()
        for movie in all_movies:
            db.session.delete(movie)

    else:
        # Just reset the stream counts
        movies_with_stream_count = Movie.query.filter(Movie.number_of_streams>0).all()
        for movie in movies_with_stream_count:
            movie.number_of_streams = 0
            db.session.add(movie)
    db.session.commit()


def main():
    """ Runs the manager.

    Target for setup.py entry point.
    """
    manager.run()


if __name__ == '__main__':
    main()
