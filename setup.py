#!/usr/bin/python3

from distutils.core import setup, Extension

wenet_ext = Extension('wenet_ext', [ 'wenet_ext.c' ])

setup(
	name = 'wenet_ext',
	version = '1.0',
	description = 'Python extension for wenet',
	ext_modules = [ wenet_ext ],
	url = 'https://www.sanslogic.co.uk',
	author = 'Philip Heron',
	author_email = 'phil@sanslogic.co.uk'
)

