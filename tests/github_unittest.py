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

    def test_comment(self):
        '''
        Adds a comment to a test issue and verifies the comment is added.
        TODO(LB): need to make sure we're mocking the github stuff for this
        (or else the tests run as slow as Chris's Mom).
        '''
        test_issue_id = 1
        comment_text = u'test comment text'
        
        config = self.client.config
        
        # add the comment
        comment_result = self.client.comment(test_issue_id, comment_text)
        
        # now verify the comment was added 
        comments = self.client.github.issues.comments(config.github_repo,
                                                            test_issue_id)
        
        # filter the comments list by id
        comment = [x for x in comments if x.id == comment_result['id']]
        
        # should only be one comment here
        self.assertTrue(len(comment) == 1)
        comment = comment[0]
        
        self.assertEqual(comment_text, comment.body)
