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
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ),
)
