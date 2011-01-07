import json
import unittest
from roundabout.config import Config
from roundabout.github.client import Client
from tests import utils


class FakeGithub(object):
    """ This fakes out the github2.Github
    """
    def __init__(self, username=None, api_token=None, requests_per_second=None):
        self.expected_value = None

    def __call__(self, *args):
        return self.expected_value

    def __getattr__(self, key, *args):
        return self


class StubbedGithub(Client):
    """
    """
    @property
    def teams(self):
        return utils.load(utils.testdata("teams.json"))

    def _get(self, *args):
        if args[0] == "pulls": 
            if len(args) == 2: # PullRequests
                return utils.load(utils.testdata("pull_requests.json"))
            elif len(args) == 3: # PullRequest
                return utils.load(utils.testdata("pull_request.json"))

class GithubClientTestCase(unittest.TestCase):
    def setUp(self):
        utils.reset_config()
        self.client = Client(conn_class=FakeGithub)

    def tearDown(self):
        utils.reset_config()

    def expect(self, ev):
        self.client.github.expected_value = ev

    def test_proper_assimilation(self):
        local_client = Client(config=Config(), conn_class=FakeGithub)
        self.assertTrue(self.client.__dict__ is local_client.__dict__)
        self.assertFalse(self.client == local_client)

    def test_stuff_with_issues(self):
        self.expect({"issues": []})
        self.assertTrue(self.client.issues)

    def test_stuff_with_branches(self):
        self.expect({"branches": []})
        self.assertTrue(self.client.branches)

    def test_github_pull_requests(self):
        client = StubbedGithub(config=Config(), conn_class=FakeGithub)
        client.config.github_core_team = "test team 1"
        pull_requests = client.pull_requests
        self.assertTrue(pull_requests)
        url, pull_request = pull_requests.items()[0]
        self.assertFalse(pull_request['lgtm'](client.approvers))

    def test_github_approvers(self):
        client = StubbedGithub(config=Config(), conn_class=FakeGithub)
        client.config.github_core_team = "test team 1"
        self.assertTrue(u'Lars Butler' in client.approvers)

    def test_github_approvers_with_bad_coreteam(self):
        self.client.config.github_core_team = "fake team"
        self.client.github.expected_value = {"foo": "bar"}
        self.assertEqual([], self.client.approvers)
