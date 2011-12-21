#!/usr/bin/python

import sys
import nose

if __name__ == '__main__':
    args = sys.argv
    args.remove(__file__)
    args = ['nosetests', '--with-coverage', '--cover-erase', '--cover-package=roundabout'] + args
    sys.path.append('tests')

    nose.run('tests', argv=args)
