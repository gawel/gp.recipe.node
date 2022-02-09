# -*- coding: utf-8 -*-
"""
This module contains the tool of gp.recipe.node
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    try:
        return open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    except:
        return ''

version = '16.13.2.1'

long_description = (
    read('README.rst')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('gp', 'recipe', 'node', 'README.rst')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.rst')
    + '\n' +
    'Download\n'
    '********\n')

entry_point = 'gp.recipe.node:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require = ['zope.testing', 'zc.buildout']

setup(name='gp.recipe.node',
      version=version,
      description="ZC Buildout recipe for node.js",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          'Framework :: Buildout',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',
          'License :: OSI Approved :: Zope Public License',
          'Development Status :: 6 - Mature',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
      ],
      keywords='buildout node.js node',
      author='Gael Pasgrimaud',
      author_email='gael@gawel.org',
      url='https://github.com/gawel/gp.recipe.node',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup', 'update_node_version']),
      namespace_packages=['gp', 'gp.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout',
                        'zc.recipe.egg',
                        'zc.recipe.cmmi',
                        'python-archive',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='gp.recipe.node.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
