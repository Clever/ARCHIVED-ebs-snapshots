#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages
from pip.req import parse_requirements
import version
import pkg_resources

here = os.path.abspath(os.path.dirname(__file__))
try:
  with open(os.path.join(here, '../README.md')) as f:
    README = f.read()
  with open(os.path.join(here, '../CHANGES.md')) as f:
    CHANGES = f.read()
except:
  README = ''
  CHANGES = ''

reqs = './requirements.txt'
if len(sys.argv) > 1 and sys.argv[1] in ['develop', 'test']:
  reqs = './requirements-dev.txt'

install_reqs = parse_requirements(os.path.join(here, reqs))

setup(name='ebs-snapshots',
      version=version.VERSION,
      description='Automates creation and removal of Amazon EBS snapshots',
      author='Clever',
      author_email='tech-notify@getclever.com',
      url='https://github.com/Clever/ebs-snapshots/',
      long_description=README + '\n\n' + CHANGES,
      packages=find_packages(exclude=['*.tests']),
      install_requires=[str(ir.req) for ir in install_reqs],
      setup_requires=['nose>=1.0'],
      test_suite='test',
      )
