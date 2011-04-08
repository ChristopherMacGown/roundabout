""" Roundabout hudson module. """

import json
import base64
import time
import urllib2

from roundabout import log


class Job(object):
    """ A Hudson Job is a configuration for CI builds. """
    def __init__(self, config, opener=None):
        self.config = config
        self.url = "%s/job/%s/api/json?depth=1" % (config.hudson_base_url,
                                                   config.hudson_job)
        self.build_url = "%s/job/%s/buildWithParameters?branch=%s"
        self.opener = opener or urllib2.urlopen # Use a test opener or urllib2

    @classmethod
    def spawn_build(cls, branch, config, opener=None):
        """
        Create and return a Hudson paramaterized build of the current job
        """
        job = cls(config, opener=opener)
        log.info("Starting hudson build on %s for %s" %
                    (job.config.hudson_job, branch))

        if job.req(job.build_url % (job.config.hudson_base_url,
                                    job.config.hudson_job, branch)):
            build_id = job.properties['nextBuildNumber']
            while True:
                # Keep trying until we return something.
                try:
                    build = [b for b in job.builds if build_id == b.number][0]
                    log.info("Build URL: %s" % build.url)
                    return build
                except IndexError:
                    time.sleep(1)

    @property
    def properties(self):
        """ Return the JSON decoded properties for this job. """
        return self.req(self.url, json_decode=True)

    @property
    def builds(self):
        """ Return the list of builds for this job. """
        return [Build(self, b) for b in self.properties['builds']]

    def req(self, url, json_decode=False):
        """
        Connect to remote url, using the provided credentials. Return either
        the result or if json_decode=True, the JSONDecoded result.
        """
        username = self.config.hudson_username
        password = self.config.hudson_password
        b64string = base64.encodestring("%s:%s" % (username, password))[:-1]
        req = urllib2.Request(url)
        req.add_header("Authorization", "Basic %s" % b64string)
        res = self.opener(req)
        
        if json_decode:
            res = json.JSONDecoder().decode(res.read())

        return res


class Build(object):
    #pylint: disable=E1101

    """ A single build for a Hudson Job """
    def __init__(self, job, b_dict):
        self.__dict__ = b_dict
        self.job = job

    def __nonzero__(self):
        return self.complete and self.success

    @property
    def complete(self):
        """ Return whether or not the build is complete. """
        return not self.building

    @property
    def success(self):
        """ Return true if self.result is 'SUCCESS' """
        return self.result == 'SUCCESS'

    def reload(self):
        """ Reload the build. """
        self.__dict__ = [b.__dict__ for b in self.job.builds 
                                          if b.number == self.number][0]
        return self
