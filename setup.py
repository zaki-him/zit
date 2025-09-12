#!/usr/bin/env python3

from setuptools import setup

setup(
  name = 'zit',
  version = '1.0',
  packages = ['zit'],
  entry_points = {
      'console_scripts' : [
          'zit = zit.cli:main'
      ]
  }
)