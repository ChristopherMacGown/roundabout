import json
import time
import unittest

import roundabout.config

from roundabout import ci
from roundabout.config import Config
from tests import utils


class FakeCIOpener(object):
    def __init__(self, *args):
        self.expected = self.__expected__

    def read(self):
        return json.dumps(self.expected)

class CITestCase(utils.TestHelper):
    class A(ci.job.Job):
        pass

    class B(object):
        pass

    def setUp(self):
        self.t = time.time()
        self.config = Config(roundabout.config.DEFAULT)

    def tearDown(self):
        print "%s: %f" % (self.id(), time.time() - self.t)

    def test_register(self):
        self.assertNothingRaised(ci.job.Job.register, 'a', self.A)
        self.assertRaises(ci.job.JobException, ci.job.Job.register, 'b', self.B)

    def test_get_job_class(self):
        self.assertRaises(ci.job.JobException, ci.job.get_ci_class, 'a')
        self.assertEqual(ci.hudson.job.Job, ci.job.get_ci_class('hudson'))
        self.assertEqual(ci.hudson.job.Job, ci.job.get_ci_class('jenkins'))

    def test_raw_job_should_raise_on_nonzero(self):
        job = ci.job.Job(self.config)
        self.assertRaises(NotImplementedError, bool, job)

    def test_raw_job_should_raise_on_url_or_complete(self):
        job = ci.job.Job(self.config)

        self.assertRaises(NotImplementedError, getattr, job, 'url')
        self.assertRaises(NotImplementedError, getattr, job, 'complete')

    def test_reload_calls_sleep(self):
        class FakeCI(FakeCIOpener):
            __expected__ = {'nextBuildNumber': 10,
                            'builds': [{'number': 10, 'url': 'http://fakeurl'}]}

        def fake_sleep(seconds):
            """ stub out time.sleep so we can make sure it's called """
            pass

        time.sleep = fake_sleep
        job = ci.job.Job.spawn('test_branch', self.config, opener=FakeCI)
        self.assertCalled(time.sleep, job.reload)

    def test_spawn(self):
        class FakeCI(FakeCIOpener):
            __expected__ = {'nextBuildNumber': 10,
                            'builds': [{'number': 10, 'url': 'http://fakeurl'}]}
        
        self.assertNothingRaised(ci.job.Job.spawn,
                                 'test_branch', self.config, opener=FakeCI)

        job = ci.job.Job.spawn('test_branch', self.config, opener=FakeCI)
        self.assertEqual(job, job.__enter__())
        self.assertEqual(None, job.__exit__())


class HudsonTestCase(utils.TestHelper):
    def setUp(self):
        self.t = time.time()
        self.config = Config(roundabout.config.DEFAULT)

    def tearDown(self):
        print "%s: %f" % (self.id(), time.time() - self.t)

    def test_hudson_specific_spawn_stuff(self):
        class FakeCI(FakeCIOpener):
            __expected__ = {'nextBuildNumber': 10,
                            'builds': [{'number': 10, 'url': 'http://fakeurl'}]}

        job = ci.job.Job.spawn('test_branch', self.config, opener=FakeCI)
        self.assertEqual(job.build, job.reload())
        self.assertEqual(job.url, FakeCI.__expected__['builds'][0]['url'])
        self.assertEqual(job.build.url, FakeCI.__expected__['builds'][0]['url'])
        self.assertEqual(job.build.number, FakeCI.__expected__['builds'][0]['number'])

    def test_successful_build(self):
        class FakeCI(FakeCIOpener):
            __expected__ = {'nextBuildNumber': 10,
                            'builds': [{'number': 10, 
                                        'building': False,
                                        'result': "SUCCESS",
                                        'url': 'http://fakeurl'}]}

        job = ci.job.Job.spawn('test_branch', self.config, opener=FakeCI)
        self.assertTrue(bool(job))
        self.assertTrue(job.reload())

    def test_waiting_build(self):
        class FakeCI(FakeCIOpener):
            __expected__ = {'nextBuildNumber': 10,
                            'builds': [{'number': 10, 
                                        'building': True,
                                        'result': '',
                                        'url': 'http://fakeurl'}]}
        job = ci.job.Job.spawn('test_branch', self.config, opener=FakeCI)
        self.assertFalse(job.build.complete)
        self.assertFalse(job.complete)
        self.assertFalse(bool(job))

    def test_failed_build(self):
        class FakeCI(FakeCIOpener):
            __expected__ = {'nextBuildNumber': 10,
                            'builds': [{'number': 10, 
                                        'building': False,
                                        'result': "",
                                        'url': 'http://fakeurl'}]}

        job = ci.job.Job.spawn('test_branch', self.config, opener=FakeCI)
        self.assertTrue(job.build.complete)
        self.assertFalse(bool(job))

    def test_spawned_hudson_build_sleeps(self):
        class FakeCI(FakeCIOpener):
            __expected__ = {'nextBuildNumber': 10, 'builds': []}

        def fake_sleep(seconds):
            """ stub out time.sleep so we can make sure it's called """
            raise RuntimeError(seconds)

        old_sleep = time.sleep
        time.sleep = fake_sleep
        try:
            self.assertCalled(time.sleep,
                              ci.job.Job.spawn,
                              'test_branch', self.config, opener=FakeCI)
        except RuntimeError:
            pass
        time.sleep = old_sleep

    def test_get_job_data(self):
        class FakeCI(FakeCIOpener):
            __expected__ = {'nextBuildNumber': 10,
                            'builds': [{'number': 10, 
                                        'building': False,
                                        'result': "SUCCESS",
                                        'url': 'http://fakeurl'}]}

        job = ci.hudson.job.Job(self.config, opener=FakeCI)
        self.assertTrue(job.properties)
