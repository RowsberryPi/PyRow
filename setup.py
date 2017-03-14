import re
from codecs import open
from os import path

from setuptools import find_packages, setup

PACKAGE_NAME = 'pyrow'
HERE = path.abspath(path.dirname(__file__))
with open(path.join(HERE, 'README.md'), encoding='utf-8') as fp:
    README = fp.read()
with open(path.join(HERE, PACKAGE_NAME, 'const.py'),
          encoding='utf-8') as fp:
    VERSION = re.search("__version__ = '([^']+)'", fp.read()).group(1)

setup(name=PACKAGE_NAME,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: Implementation :: CPython',
          'Topic :: Utilities'],
      description=('PyRow is a Python library that allows interaction with '
                   'a Concept2 PM3, PM4 or PM5.'),
      install_requires=['pyusb >= 1.0.0'],
      keywords='rowing ergometer concept2',
      license='Simplified BSD License',
      long_description=README,
      package_data={'': ['LICENSE'], PACKAGE_NAME: ['*.ini']},
      packages=find_packages(exclude=['tests']),
      test_suite='tests',
      version=VERSION)
