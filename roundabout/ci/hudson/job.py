""" Roundabout hudson/jenkins module. """

import json
import base64
import time
import urllib2

from roundabout import log
from roundabout.ci import job
from roundabout.ci.hudson import build


class Job(job.Job):
    """ A Hudson Job is a configuration for CI builds. """
    def __init__(self, config, opener=None):
        super(Job, self).__init__(config, opener)

        self.build = None
        self.job_endpoint = "%s/job/%s/api/json?depth=1" % (
                                    config["ci"]["base_url"],
                                    config["ci"]["job"])
        self.build_endpoint = "%s/job/%s/buildWithParameters?branch=%s"

    def __nonzero__(self):
        return bool(self.build)

    @classmethod
    def spawn(cls, branch, config, opener=None):
        """
        Create and return a paramaterized build of the current job
        """

        _job = cls(config, opener=opener)
        log.info("Building: %s for %s" % (_job.config["ci"]["job"], branch))

        if _job.req(_job.build_endpoint % (_job.config["ci"]["base_url"],
                                         _job.config["ci"]["job"], branch)):
            build_id = _job.properties['nextBuildNumber']
            while True:
                # Keep trying until we return something.
                try:
                    _job.build = [b for b
                                    in _job.builds
                                    if build_id == b.number][0]
                    log.info("Build URL: %s" % _job.url)
                    return _job
                except IndexError:
                    time.sleep(1)

    @property
    def builds(self):
        """ Return the list of builds for this job. """
        return [build.Build(self, b) for b in self.properties['builds']]

    @property
    def properties(self):
        """ Return the JSON decoded properties for this job. """
        return self.req(self.job_endpoint, json_decode=True)

    @property
    def url(self):
        """ Return the URL of our build """
        return self.build.url

    @property
    def complete(self):
        """ Return true if the build is complete """
        return self.build.complete

    def reload(self):
        """ call ci.job.Job.reload to sleep, then reload the build."""
        super(Job, self).reload()
        return self.build.reload()

    def req(self, url, json_decode=False):
        """
        Connect to remote url, using the provided credentials. Return either
        the result or if json_decode=True, the JSONDecoded result.
        """
        username = self.config["ci"]["username"]
        password = self.config["ci"]["password"]
        b64string = base64.encodestring("%s:%s" % (username, password))[:-1]
        req = urllib2.Request(url)
        req.add_header("Authorization", "Basic %s" % b64string)

        try:
            res = self.opener(req)
        except Exception as e:
            contents = e.read()
            log.error(contents) # http errors have content bodies... like servlet
                                # container stacktraces. I'm looking at you, 
                                # Jenkins... -grue
            raise e

        if json_decode:
            res = json.loads(res.read())

        return res


job.Job.register('hudson', Job)
job.Job.register('jenkins', Job)

