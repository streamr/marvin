"""
    marvin.management
    ~~~~~~~~~~~~~~~~~

    Configures the manager, and acts as an entry point for the manage command.

"""
# pylint: disable=invalid-name
from . import create_app, db, init_db

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


def main():
    """ Runs the manager.

    Target for setup.py entry point.
    """
    manager.run()


if __name__ == '__main__':
    main()
