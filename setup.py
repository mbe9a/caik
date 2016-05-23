'''
Alex Arsenovic, Michael Eller, Noah Sauber
UVA THZ CAI
'''

#!/usr/bin/env python
import os
from setuptools import setup

VERSION = '1.3'
LONG_DESCRIPTION = """
		caik is a collection of python code to take and decode data in a coded aperture imaging project.
"""

setup(
	name='caik',
	version=VERSION,
	description='Object Oriented Coded Aperture Imaging',
	long_description=LONG_DESCRIPTION,
	author='Michael Eller',
	author_email='mbe9a@virginia.edu',
	py_modules = ['caik', 'instruments', 'cai', 'decoder'],
	#package_dir= {'','cat'},
	)
