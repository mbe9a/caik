#!/usr/bin/env python
from setuptools import setup, find_packages
from distutils.core import Extension

VERSION = '0.1.0'
LONG_DESCRIPTION = """
		cai-kit is a collection of python code to take and decode data in a coded aperture project imaging project.
"""

setup(name='scikit-rf',
	version=VERSION,
	description='Object Oriented Coded Aperture Imaging',
	long_description=LONG_DESCRIPTION,
	author='Michael Eller',
	author_email='mbe9a@virginia.edu',
	packages=find_packages(),
	install_requires = [
		'scikit-rf',
		'numpy',
		'pyvisa',
		'matplotlib',
		],
	package_dir={'cat':'cat'},
	include_package_data = True,
	)
