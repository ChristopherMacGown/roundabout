import unittest
from roundabout.config import Config
from roundabout.github import scraper
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


class GithubScraperTestCase(unittest.TestCase):
    def setUp(self):
        utils.reset_config()
        Config()

        with open(utils.testdata("pull_requests.html")) as f:
            self.pull_requests = f.read()
            
        with open(utils.testdata("pull_request.html")) as f:
            self.pull_request = f.read()

    def tearDown(self):
        utils.reset_config()

    def test_parse_pull_requests(self):
        # TODO(chris): Mock the connection to GH so we don't end up getting 
        # stuff from live instead of the test data

        commits = ['e17e2a07a94724f675e99d670d98b87431883fd7', 
                   '93e19157354d5107b65e9f9292d41a6a10528bd3',
                   'f732094b25e9a3e67dfb5da360c17771dfd28ca5',
                   '0be6240672416367581dcea1f9abb2b5ba470d75']
        comments = [{'body': 'Just a test comment.', 
                     'author': 'ChristopherMacGown'}]
        remote_name = 'larsbutler'
        remote_branch = 'master'
        remote_url = 'https://ChristopherMacGown@github.com/larsbutler/roundabout.git'
        pull_request = scraper.PullRequest(commits, comments, remote_name,
            remote_branch, remote_url)
        expected = {'https://github.com/ChristopherMacGown/roundabout/pull/2': pull_request}
        self.assertEqual(expected, scraper.parse_pull_requests(
            self.pull_requests))

    def test_parse_pull_request_page(self):
        commits = ['e17e2a07a94724f675e99d670d98b87431883fd7']
        comments = []
        remote_name = 'larsbutler'
        remote_branch = 'master'
        remote_url ='https://ChristopherMacGown@github.com/larsbutler/roundabout.git'
        expected = scraper.PullRequest(commits, comments, remote_name,
                remote_branch, remote_url)

        self.assertEqual(expected, scraper.parse_pull_request_page(
            self.pull_request))
