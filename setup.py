#!/usr/bin/env python

import os
import sys

import fannypack

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = [
    'fannypack',
]

requires = [
    'flask'
]

with open('README.md') as f:
    readme = f.read()

setup(
    name='fannypack',
    version=fannypack.__version__,
    description='a set of utilities for flask',
    long_description=readme + '\n\n',
    author='Andrei',
    author_email='andrei.zbikowski@gmail.com',
    url='http://github.com/b1naryth1ef/fannypack',
    packages=packages,
    package_data={},
    package_dir={'fannypack': 'fannypack'},
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
