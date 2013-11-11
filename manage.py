"""
    Entrypoint for running scripts. List available actions by running `python manage.py -h`.

    The actions themselves are defined in marvin.management.py.
"""

from marvin.management import manager

if __name__ == '__main__':
    manager.run()
