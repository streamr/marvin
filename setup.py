#!/usr/bin/env python
# coding: utf-8
"""
    setup.py
    ~~~~~~~~

    Installs marvin as a package.

"""

from setuptools import setup, find_packages

setup(
    name='marvin',
    version='0.1.0',
    author='Tarjei Husøy',
    author_email='tarjei@roms.no',
    url='https://github.com/streamr/marvin',
    description='API endpoints for streamr',
    packages=find_packages(),
    package_data={
        '': [
            'log_conf.yaml',
            'templates/*.html',
        ],
    },
    zip_safe=False,
)
