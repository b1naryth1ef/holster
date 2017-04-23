#!/usr/bin/env python

import os
import sys

import holster

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = [
    'holster',
]

requires = [
    'six'
]

setup(
    name='holster',
    version=holster.__version__,
    description='a set of Python utilities',
    long_description='',
    author='Andrei',
    author_email='andrei.zbikowski@gmail.com',
    url='http://github.com/b1naryth1ef/holster',
    packages=packages,
    package_data={},
    package_dir={'holster': 'holster'},
    include_package_data=True,
    install_requires=requires,
    license='Apache 2.0',
    zip_safe=False,
)
