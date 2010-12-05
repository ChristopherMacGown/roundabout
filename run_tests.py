import sys
import nose

if __name__ == '__main__':
    args = ['nosetests', '--with-coverage', '--cover-package=roundabout', "-s"]
    sys.path.append('tests')

    nose.run('tests', argv=args)
