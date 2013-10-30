#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages
from os import path

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
        ],
    },
    zip_safe=False,
)
