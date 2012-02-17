import json
import os
import time
import unittest


from roundabout.models import pull_request
from tests import utils

class PullRequestTestCase(utils.TestHelper):
    def setUp(self):
        self.pr_path = utils.testdata('output/pulls')

    def tearDown(self):
        pass

    def test_create_a_new_pull_request(self):
        pr_str = utils.load(utils.testdata('new_pull_request.json'))
        pr = pull_request.PullRequest(pr_str, self.pr_path)

        self.assertNothingRaised(pr.save,)
        self.assertTrue(os.path.exists(os.path.join(self.pr_path, "2", "pull.js")))
        pr2 = pull_request.PullRequest.load(os.path.join(self.pr_path, "2"))
        self.assertEqual(pr._pull_request, pr2._pull_request)

    def test_check_its_comments(self):
        pr = pull_request.PullRequest.load(os.path.join(self.pr_path, "2"))

        self.assertEqual([], list(pr.comments))

