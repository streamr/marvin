"""
    marvin.management
    ~~~~~~~~~~~~~~~~~

    Configures the manager, and acts as an entry point for the manage command.

"""
# pylint: disable=invalid-name
from . import create_app, db

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app()
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

def main():
    """ Runs the manager.

    Target for setup.py entry point.
    """
    manager.run()


if __name__ == '__main__':
    main()
