import unittest
from roundabout.config import Config
from roundabout.github import scraper
from roundabout.github.client import Client
from tests import utils

class GithubClientTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_proper_assimilation(self):
        local_client = Client()
        self.assertTrue(self.client.__dict__ is local_client.__dict__)
        self.assertFalse(self.client == local_client)

    def test_github_connection(self):
        self.assertTrue(self.client.issues)
        self.assertTrue(self.client.branches)

    def test_github_pull_requests(self):
        self.assertTrue(self.client.pull_requests)


class GithubScraperTestCase(unittest.TestCase):
    def setUp(self):
        with open(utils.testdata("pull_requests.html")) as f:
            self.pull_requests = f.read()
            
        with open(utils.testdata("pull_request.html")) as f:
            self.pull_request = f.read()

    def test_parse_pull_requests(self):
        expected = {'https://github.com/ChristopherMacGown/roundabout/pull/2':
                    ['e17e2a07a94724f675e99d670d98b87431883fd7']}
        self.assertEqual(expected, scraper.parse_pull_requests(
            self.pull_requests))

    def test_parse_pull_request_commits(self):
        expected = ['e17e2a07a94724f675e99d670d98b87431883fd7']
        self.assertEqual(expected, scraper.parse_pull_request_commits(
            self.pull_request))
