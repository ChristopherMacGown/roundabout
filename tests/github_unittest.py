import unittest
from roundabout.config import Config
from roundabout.github import Client
from tests import utils

class GithubClientTestCase(unittest.TestCase):
    def setUp(self):
        utils.reset_config()
        self.client = Client()

    def tearDown(self):
        utils.reset_config()

    def test_proper_assimilation(self):
        local_client = Client()
        self.assertTrue(self.client.__dict__ is local_client.__dict__)
        self.assertFalse(self.client == local_client)

    def test_github_connection(self):
        self.assertTrue(self.client.issues)
        self.assertTrue(self.client.branches)
