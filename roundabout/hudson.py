import json
import base64
import time
import urllib2
from urlparse import urlparse

from roundabout import log
from roundabout.config import Config

class Job(object):
    def __init__(self, config=Config(), opener=None):
        self.config = config
        self.url = "%s/job/%s/api/json?depth=1" % (config.hudson_base_url,
                                                   config.hudson_job)

        self.build_url = "%s/job/%s/buildWithParameters?branch=%s"
        self.opener = opener or urllib2.urlopen # Use a test opener or urllib2
        log.info("Build URL: %s" % self.url)

    @classmethod
    def spawn_build(cls, branch, opener=None):
        job = cls(opener=opener)
        log.info("Starting hudson build on %s for %s" %
                    (job.config.hudson_job, branch))

        if job.req(job.build_url % (job.config.hudson_base_url,
                                    job.config.hudson_job, branch)):
            build_id = job.properties['nextBuildNumber']
            while True:
                # Keep trying until we return something.
                try:
                    return [build for build 
                                  in job.builds 
                                  if build_id == build.number][0]
                except IndexError:
                    if opener:
                        raise
                    else:
                        time.sleep(1)

    @property
    def properties(self):
        return self.req(self.url, json_decode=True)

    @property
    def builds(self):
        return [Build(self, b) for b in self.properties['builds']]

    def req(self, url, json_decode=False):
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
    def __init__(self, job, b_dict):
        self.__dict__ = b_dict
        self.job = job

    def __nonzero__(self):
        return self.complete and self.success

    @property
    def complete(self):
        return not self.building

    @property
    def success(self):
        return self.result == 'SUCCESS'

    def reload(self):
        self.__dict__ = [b.__dict__ for b in self.job.builds if b.number == self.number][0]
        return self
