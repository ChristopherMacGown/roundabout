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
        print Config.__shared_state__
        self.assertTrue(self.client.issues)
        self.assertTrue(self.client.branches)

    def test_github_pull_requests(self):
        self.assertTrue(self.client.pull_requests)

    def test_github_approvers(self):
        self.assertTrue(u'Lars Butler' in self.client.approvers)
