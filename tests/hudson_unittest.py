import unittest
from roundabout.hudson import Job

class HudsonTestCase(unittest.TestCase):
    def test_fail_this_for_hudson(self):
        self.asserFalse(True)

    def test_get_spawn_build(self):
        job = Job.spawn_build('test_branch')
        self.assertTrue(job.number)

    def test_get_job_data(self):
        job = Job()
        self.assertTrue(job.properties)

    def test_build_success(self):
        job = Job()
        build1 = [b for b in job.builds if b.number == 1][0]
        build2 = [b for b in job.builds if b.number == 2][0]

        self.assertFalse(build1)
        self.assertTrue(build2)
