#!/usr/bin/env python

from distutils.core import setup
from setuptools import setup, find_packages

setup(version='0.12',
      description='Scala source analysis tools from foursquare',
      author='Benjy W',
      author_email='benjy@foursquare.com',
      url='https://www.python.org/sigs/distutils-sig/',
      name = 'scala-source-tools',
      packages = find_packages(),
      scripts = ['scripts/git-fix-scala-imports.sh'],
      entry_points = {
        'console_scripts': [
          'scala_import_sorter = foursquare.source_code_analysis.scala.scripts.scala_import_sorter:main'
        ]
      }
     )
