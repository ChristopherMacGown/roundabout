from distutils.core import setup
from setuptools import find_packages

setup(name='roundabout',
      version='0.8',
      description='roundabout ',
      authors=['Christopher MacGown', 'Lars Butler', 'hub-cap'],
      author_email='roundabout-dev@googlegroups.com',
      url='',
      packages=['roundabout', 'roundabout/github', 'roundabout/ci', 'roundabout/ci/hudson'],
      scripts = ['bin/roundabout'],
      data_files=[('/etc/roundabout', ['roundabout.cfg',
                                       'roundabout.cfg-example'])],
      install_requires=["coverage", "nose", "github2>=0.4.1", "gitpython", "pylint"])
