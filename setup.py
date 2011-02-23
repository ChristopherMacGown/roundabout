from distutils.core import setup
from setuptools import find_packages

setup(name='roundabout',
      version='0.15',
      description='roundabout ',
      authors=['Christopher MacGown', 'Lars Butler'],
      author_email='roundabout-dev@googlegroups.com',
      url='',
      packages=['roundabout', 'roundabout/github'],
      scripts = ['bin/roundabout'],
      install_requires=["coverage", "nose", "github2", "gitpython", "pylint"])
