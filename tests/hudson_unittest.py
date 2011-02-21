import json
import time
import unittest

import roundabout.config

from roundabout.config import Config
from roundabout.hudson import Job
from tests import utils

class HudsonTestCase(utils.TestHelper):
    def setUp(self):
        self.t = time.time()
        self.config = Config(roundabout.config.DEFAULT)

    def tearDown(self):
        print "%s: %f" % (self.id(), time.time() - self.t)

    def test_get_spawn_build(self):
        class FakeHudson(object):
            def __init__(self, *args):
                self.expected = {'nextBuildNumber': 10,
                                 'builds': [
                                     {'number': 10}
                                  ]}
            def read(self):
                return json.JSONEncoder().encode(self.expected)
        
        job = Job.spawn_build('test_branch', self.config, opener=FakeHudson)
        self.assertTrue(job.number)

    def test_get_spawn_build_gets_into_the_sleep(self):
        class FakeHudson(object):
            def __init__(self, *args):
                self.expected = {'nextBuildNumber': 10,
                                 'builds': []}
            def read(self):
                return json.JSONEncoder().encode(self.expected)

        def fake_sleep(seconds):
            """ stub out time.sleep so we can make sure it's called """
            raise RuntimeError(seconds)

        time.sleep = fake_sleep
        try:
            self.assertCalled(time.sleep,
                              Job.spawn_build,
                              'test_branch', self.config, opener=FakeHudson)
        except RuntimeError:
            pass

    def test_get_job_data(self):
        job = Job(self.config)
        self.assertTrue(job.properties)

    def test_build_success(self):
        job = Job(self.config)
        build1 = [b for b in job.builds if b.number == 1][0]
        build2 = [b for b in job.builds if b.number == 2][0]

        self.assertFalse(build1)
        self.assertTrue(build2)
        self.assertTrue(build2.reload())
