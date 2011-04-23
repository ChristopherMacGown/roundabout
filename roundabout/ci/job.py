""" Roundabout CI job module. """

import json
import base64
import time
import urllib2

from roundabout import log


class JobException(Exception):
    pass


class Job(object):
    """ A Hudson Job is a configuration for CI builds. """
    __job_classes__ = {}

    def __init__(self, config, opener=None):
        self.config = config
        self.opener = opener or urllib2.urlopen # Use a test opener or urllib2

    def __nonzero__(self):
        raise NotImplementedError("Descendent classes should implement this")

    def __enter__(self):
        return self

    def __exit__(self):
        pass

    @classmethod
    def get_ci_class(cls, config_param):
        try:
            return cls.__job_classes__[config_param]
        except KeyError:
            raise JobException("No class registered to handle %s" % config_param)

    @classmethod
    def register(cls, name, job_class):
        if not issubclass(job_class, cls):
            raise JobException("Cannot register %s, not a Job" % job_class)

        cls.__job_classes__[name] = job_class

    @classmethod
    def spawn(cls, branch, config, opener=None):
        """
        Create and return a paramaterized Job based on the CI config.
        """

        job_class = cls.get_ci_class(config.ci_class)
        log.info("Starting %s job" % config.ci_class)

        return job_class.spawn(branch, config, opener)
