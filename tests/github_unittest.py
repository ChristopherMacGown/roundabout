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
        self.config = Config()
        self.client = Client(conn_class=FakeGithub,
                             config=self.config)

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
        self.expect({"foo": "bar"})
        self.assertEqual([], self.client.approvers)

    def test_comment(self):
        '''
        Adds a comment to a test issue and verifies the comment is added.
        TODO(LB): need to change the test setup so we're mocking the github 
        stuff for this (or else the tests run as slow as Chris's Mom).
        '''

        class Comment(object):
            def __init__(self, dictionary):
                self.__dict__ = dictionary

        test_issue_id = 12345
        comment_text = u'test comment text'
        
        # add the comment
        self.expect(utils.load(utils.testdata('comment.json')))
        comment_result = self.client.comment(test_issue_id, comment_text)
    
        # now verify the comment was added 
        self.expect([Comment(x) for x 
            in utils.load(utils.testdata('comments.json'))["comments"]])
        comments = self.client.github.issues.comments(self.config.github_repo,
                                                            test_issue_id)
        
        # filter the comments list by id
        comment = [x for x in comments if x.id == comment_result['id']]
        
        # should only be one comment here
        self.assertTrue(len(comment) == 1)
        comment = comment[0]
        
        self.assertEqual(comment_text, comment.body)

    def test_reject(self):
        class Issue(object):
            def __init__(self, dictionary):
                self.__dict__ = dictionary

        def _get_issue(issue_id):
            return self.client.github.issues.show(self.config.github_repo,
                                                  issue_id)

        test_pr_id = 1
        reject_message = u'Merge failed'

        # TODO(LB): temporary -- repoen the pull request for this test
        # Remove this line once github mocking is in place
        self.expect(Issue(utils.load(utils.testdata('issue_open.json'))['issue']))
        self.client.github.issues.reopen(self.config.github_repo,
                                         test_pr_id)
        # verify the issue is open
        issue = _get_issue(test_pr_id)
        self.assertEqual(u'open', issue.state)
        
        # TODO(LB): need to mock up github here as well; see test_comment()
        self.expect(Issue(utils.load(utils.testdata('issue_closed.json'))['issue']))
        rejected_issue = self.client.reject(test_pr_id, reject_message)
        self.assertEqual(u'closed', rejected_issue.state)
