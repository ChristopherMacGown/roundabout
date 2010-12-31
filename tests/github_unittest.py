import unittest
from roundabout.config import Config
from roundabout.github.client import Client
from tests import utils

class GithubClientTestCase(unittest.TestCase):
    def setUp(self):
        utils.reset_config()
        self.client = Client(config=Config())

    def tearDown(self):
        utils.reset_config()

    def test_proper_assimilation(self):
        local_client = Client()
        self.assertTrue(self.client.__dict__ is local_client.__dict__)
        self.assertFalse(self.client == local_client)

    def test_github_connection(self):
        self.assertTrue(self.client.issues)
        self.assertTrue(self.client.branches)

    def test_github_pull_requests(self):
        #TODO(chris): Stub out github API so I can test that lgtm works without.
        pull_requests = self.client.pull_requests
        self.assertTrue(pull_requests)
        self.assertFalse(pull_requests[0].lgtm(self.client.approvers))

    def test_github_approvers(self):
        self.assertTrue(u'Lars Butler' in self.client.approvers)

    def test_github_approvers_with_bad_coreteam(self):
        self.client.config.github_core_team = "fake team"
        self.assertEqual([], self.client.approvers)
