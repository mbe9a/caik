'''
Alex Arsenovic, Michael Eller, Noah Sauber
UVA THZ CAI
'''

from setuptools import setup, find_packages
from distutils.core import Extension


with open('caik/__init__.py') as fid:
    for line in fid:
        if line.startswith('__version__'):
            VERSION = line.strip().split()[-1][1:-1]
            break

LONG_DESCRIPTION = """
	caik is a python module currently being developed for the UVa terahertz vector coded aperture imaging project.
"""
setup(name='caik',
	version=VERSION,
	license='new BSD',
	description='Object Oriented VECAP',
	long_description=LONG_DESCRIPTION,
	author='Michael Eller',
	author_email='mbe9a@virginia.edu',
	packages=find_packages(),
	install_requires = [
		'ipython',
		'numpy',
		'scipy',
        'pandas',
		'matplotlib',
		'scikit-rf',
		'python-ivi',
		'pyvisa',
		'xarray',
		'unipath'
		],
	package_dir={'caik':'caik'},
	include_package_data = True
	)
