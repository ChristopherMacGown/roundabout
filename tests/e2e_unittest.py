import unittest
from roundabout.github.client import Client


class EndToEnd(unittest.TestCase):
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_end_to_end(self):
        """
        setUp:
            Create mergeable pull requests, including:
                successful builds
                unsuccessful builds
            Create unmergeable pull requests
        
        Test that expected approved pull requests are found
        For each pull request:
            Create a remote branch
            Test remote branch is created
            Fetch the remote branch
            Checkout the branch to local
            Test that local checkout succeeds
            Merge master (to local branch)
            if mergeable pull req.:
                assert merge success
                push to remote branch
                spawn hudson job to build the incoming code
                checkout master
                wait for hudson build to complete
                assert build result (see setUp)
                if succesful build:
                    merge the remote branch
                    verify?
                    push to master
                    verify?
                elif unsuccessful build:
                    reject the pull request
                    verify rejected
            elif unmergeable pull req.:
                assert merge failure
                reject the pull request
                verify rejected
        """
        github = Client()
        
        # get all current pull requests
        all_pull_requests = github.pull_requests
        
        # find the approved PRs
        approved_prs = [pr for pr in all_pull_requests
                            if p.lgtm(github.approvers)]

        # TODO: verify that the current approved PRs are as expected
        
