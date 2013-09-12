#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from setuptools import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='keychain_manager',
    version='0.1.0',
    description='A Python api for Mac OS X Keychain, '
    'heavily inspired by https://github.com/jprichardson/keychain_manager',
    long_description=readme + '\n\n' + history,
    author='Andrii Kurinnyi',
    author_email='andrew@marpasoft.com',
    url='https://github.com/zen4ever/keychain_manager',
    packages=[
        'keychain_manager',
    ],
    package_dir={'keychain_manager': 'keychain_manager'},
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='keychain_manager',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
)
