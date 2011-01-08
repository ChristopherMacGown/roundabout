import unittest
from roundabout.config import Config
from roundabout.github.client import Client
from tests import utils

class GithubClientTestCase(unittest.TestCase):
    def setUp(self):
        utils.reset_config()
        self.config = Config()
        self.client = Client(self.config)

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

    def test_comment(self):
        '''
        Adds a comment to a test issue and verifies the comment is added.
        TODO(LB): need to change the test setup so we're mocking the github 
        stuff for this (or else the tests run as slow as Chris's Mom).
        '''
        test_issue_id = 1
        comment_text = u'test comment text'
        
        # add the comment
        comment_result = self.client.comment(test_issue_id, comment_text)
        
        # now verify the comment was added 
        comments = self.client.github.issues.comments(self.config.github_repo,
                                                            test_issue_id)
        
        # filter the comments list by id
        comment = [x for x in comments if x.id == comment_result['id']]
        
        # should only be one comment here
        self.assertTrue(len(comment) == 1)
        comment = comment[0]
        
        self.assertEqual(comment_text, comment.body)

    def test_reject(self):
        def _get_issue(issue_id):
            return self.client.github.issues.show(self.config.github_repo,
                                                  issue_id)

        test_pr_id = 11 # TODO(LB): update me once we have mocked github + data
        reject_message = u'Merge failed'

        # TODO(LB): temporary -- repoen the pull request for this test
        # Remove this line once github mocking is in place
        self.client.github.issues.reopen(self.config.github_repo,
                                         test_pr_id)
        # verify the issue is open
        issue = _get_issue(test_pr_id)
        self.assertEqual(u'open', issue.state)
        
        # TODO(LB): need to mock up github here as well; see test_comment()
        rejected_issue = self.client.reject(test_pr_id, reject_message)
        self.assertEqual(u'closed', rejected_issue.state)
