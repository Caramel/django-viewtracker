#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='django-viewtracker',
    version='1.0',
    description='Object view tracker for Django',
    author='Michael Farrell',
    author_email='michael+dvt@uanywhere.com.au',
    url='http://uanywhere.com.au/',
    packages=[
        'viewtracker',
    ],
    classifiers=[
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Utilities'],
)
