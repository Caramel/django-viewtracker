#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
	name='django-viewtracker',
	version='1.2',
	description='Object view tracker for Django',
	author='Caramel',
	author_email='support@caramel.com.au',
	url='https://github.com/Caramel/django-viewtracker',
	packages=[
		'viewtracker',
	],
	license='BSD',
	classifiers=[
		'Environment :: Web Environment',
		'Framework :: Django',
		'Intended Audience :: Developers',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Utilities'
	],
)

