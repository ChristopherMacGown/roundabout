import json
import time
import unittest

import roundabout.config

from roundabout.config import Config
from roundabout.github.client import Client
from tests import utils


class FakeGithub(object):
    """ This fakes out the github2.Github
    """
    def __init__(self, username=None, api_token=None, requests_per_second=None,
                 proxy_host=None, proxy_port=None):
        self.expected_value = None

    def __call__(self, *args):
        return self.expected_value

    def __getattr__(self, key, *args):
        return self


class StubbedGithub(Client):
    """
    """

    def __init__(self, *args, **kwargs):
        super(StubbedGithub, self).__init__(*args, **kwargs)
        self.pull_request_files = ("pull_requests.json", "pull_request.json")

    @property
    def teams(self):
        return utils.load(utils.testdata("teams.json"))

    def get(self, *args):
        if args[0] == "pulls": 
            if len(args) == 2: # PullRequests
                return utils.load(utils.testdata(self.pull_request_files[0]))
            elif len(args) == 3: # PullRequest
                return utils.load(utils.testdata(self.pull_request_files[1]))


class GithubClientTestCase(unittest.TestCase):
    def setUp(self):
        self.t = time.time()
        self.config = Config(roundabout.config.DEFAULT)
        print self.config
        self.client = Client(conn_class=FakeGithub,
                             config=self.config)

    def tearDown(self):
        print "%s: %f" % (self.id(), time.time() - self.t)

    def expect(self, ev):
        self.client.github.expected_value = ev

    def test_proper_assimilation(self):
        local_client = Client(config=self.config, conn_class=FakeGithub)
        self.assertTrue(self.client.__dict__ is local_client.__dict__)
        self.assertFalse(self.client == local_client)

    def test_stuff_with_issues(self):
        self.expect({"issues": []})
        self.assertTrue(self.client.issues)

    def test_stuff_with_branches(self):
        self.expect({"branches": []})
        self.assertTrue(self.client.branches)

    def test_github_pull_requests(self):
        client = StubbedGithub(config=self.config, conn_class=FakeGithub)
        client.config["github"]["core_team"] = "test team 1"
        pull_requests = client.pull_requests
        self.assertTrue(pull_requests)

        for url, pull in pull_requests.items():
            self.assertEqual("master", pull.remote_branch)
            self.assertEqual("master", pull.base_branch)
            self.assertEqual("larsbutler", pull.remote_name)
            self.assertEqual("https://github.com/larsbutler/roundabout.git",
                             pull.remote_url)

            pull.username = "fake"
            pull.password = "fake"

            self.assertEqual("https://fake:fake@github.com/larsbutler/"
                             "roundabout.git", pull.remote_url)

    def test_lgt_robots(self):
        client = StubbedGithub(config=self.config, conn_class=FakeGithub)
        client.config["github"]["username"] = "Bender B. Rodriguez"
        client.config["default"]["premerge_robo_lgtm"] = "ROBOTICALLY APPROVED PRE-MERGE. BEEP BOOP."

        def test_with_robotic_approval():
            self.assertTrue([p for (url, p)
                               in client.pull_requests.items()
                               if p.looks_good_to_a_robot("Bender B. Rodriguez")])

        def test_without_robotic_approval():
            self.assertFalse([p for (url, p)
                               in client.pull_requests.items()
                               if p.looks_good_to_a_robot("Phillip J. Fry (Who is not a robot)")])
        
        def test_with_robots_saying_irrelevant_things():
            client.config["default"]["premerge_robo_lgtm"] = "This is not the pre-merge robo-shibboleth."
            self.assertTrue([p for (url, p)
                               in client.pull_requests.items()
                               if p.looks_good_to_a_robot("Bender B. Rodriguez")])

        test_with_robotic_approval()
        test_without_robotic_approval()


    def test_lgtm(self):
        client = StubbedGithub(config=self.config, conn_class=FakeGithub)
        client.config["github"]["core_team"] = "test team 1"

        def test_lgtm_without_reject():
            self.assertTrue([p for (url, p)
                               in client.pull_requests.items()
                               if p.looks_good_to_a_human(client.approvers)])

        def test_no_lgtm_after_reject_should_fail():
            client.pull_request_files = ("unlgtmed_pull_requests_with_rej.json", 
                                         "unlgtmed_pull_request_with_rej.json")

            rej = [c.get('body', '') for c in client.pull_requests.items()[0][1].discussion][-1]

            self.assertFalse([p for (url, p)
                                in client.pull_requests.items()
                                if p.looks_good_to_a_human(client.approvers)])


        def test_lgtm_after_reject():
            client.pull_request_files = ("lgtmed_pull_requests_with_rej.json", 
                                         "lgtmed_pull_request_with_rej.json")

            [(url, p)] = client.pull_requests.items()

            self.assertTrue([p for (url, p)
                               in client.pull_requests.items()
                               if p.looks_good_to_a_human(client.approvers)])

        test_lgtm_without_reject()
        test_no_lgtm_after_reject_should_fail()
        test_lgtm_after_reject()


    def test_github_approvers(self):
        client = StubbedGithub(config=self.config, conn_class=FakeGithub)
        client.config["github"]["core_team"] = "test team 1"
        self.assertTrue(u'larsbutler' in client.approvers)

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

        client = StubbedGithub(config=self.config, conn_class=FakeGithub)
        client.config["github"]["core_team"] = "test team 1"
        pull_request = client.pull_requests.values()[0]

        test_issue_id = 12345
        comment_text = u'test comment text'
        
        # add the comment
        self.expect(utils.load(utils.testdata('comment.json')))
        comment_result = pull_request.comment(comment_text)
    
        # now verify the comment was added 
        self.expect([Comment(x) for x 
            in utils.load(utils.testdata('comments.json'))["comments"]])
        comments = self.client.github.issues.comments(self.config["github"]["repo"],
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
            return self.client.github.issues.show(self.config["github"]["repo"],
                                                  issue_id)

        test_pr_id = 1
        reject_message = u'Merge failed'

        # TODO(LB): temporary -- repoen the pull request for this test
        # Remove this line once github mocking is in place
        self.expect(Issue(utils.load(utils.testdata('issue_open.json'))['issue']))
        self.client.github.issues.reopen(self.config["github"]["repo"],
                                         test_pr_id)
        # verify the issue is open
        issue = _get_issue(test_pr_id)
        self.assertEqual(u'open', issue.state)
        
        # TODO(LB): need to mock up github here as well; see test_comment()
        client = StubbedGithub(config=self.config, conn_class=FakeGithub)
        client.config.github_core_team = "test team 1"
        pull_request = client.pull_requests.values()[0]

        self.expect(Issue(utils.load(utils.testdata('issue_closed.json'))['issue']))
        rejected_issue = pull_request.close(reject_message)
        self.assertEqual(u'closed', rejected_issue.state)

