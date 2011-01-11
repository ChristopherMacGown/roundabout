import time
import unittest
from roundabout.config import Config
from roundabout.git import Git, GitException
from tests import utils

class GitTestCase(unittest.TestCase):
    def setUp(self):
        self.t = time.time()
        utils.reset_config()

    def tearDown(self):
        print "%s: %f" % (self.id(), time.time() - self.t)
        utils.reset_config()

    def test_clone_repo_with_good_config(self):
        config = Config(config_files=[utils.testdata('good_git.cfg')])
        remote_name = config.git_test_remote_name
        remote_url = config.git_test_remote_url
        remote_branch = config.git_test_remote_branch
        repo = Git(remote_name=remote_name,
                   remote_url=remote_url,
                   remote_branch=remote_branch)
        self.assertTrue(repo)

    def test_enter_repo_with_good_config(self):
        config = Config(config_files=[utils.testdata('good_git.cfg')])
        remote_name = config.git_test_remote_name
        remote_url = config.git_test_remote_url
        remote_branch = config.git_test_remote_branch

        git = Git(remote_name=remote_name,
                  remote_url=remote_url,
                  remote_branch=remote_branch)
        git.repo.create_head(git.remote_branch)
        self.assertTrue(git.__enter__())
        self.assertTrue(git.branch('master').checkout())
        self.assertFalse(git.__exit__())

    def test_clean_merge_with_good_config(self):
        config = Config(config_files=[utils.testdata('good_git.cfg')])
        remote_name = config.git_test_remote_name
        remote_url = config.git_test_remote_url
        remote_branch = config.git_test_remote_branch

        git = Git(remote_name=remote_name,
                  remote_url=remote_url,
                  remote_branch=remote_branch)
        git.repo.create_head(git.remote_branch)

        with git as repo:
            self.assertTrue(git.merge('master'))
            self.assertTrue(git.branch('master').checkout())

    def test_push_with_good_config(self):
        config = Config(config_files=[utils.testdata('good_git.cfg')])
        remote_name = config.git_test_remote_name
        remote_url = config.git_test_remote_url
        remote_branch = config.git_test_remote_branch

        repo = Git(remote_name=remote_name,
                   remote_url=remote_url,
                   remote_branch=remote_branch)

        self.assertTrue(repo.push('master'))

    def test_clone_repo_with_bad_config(self):
        config = Config(config_files=[utils.testdata('bad_git.cfg')])
        remote_name = config.git_test_remote_name
        remote_url = config.git_test_remote_url
        remote_branch = config.git_test_remote_branch

        self.assertRaises(GitException, Git, remote_name, remote_url, remote_branch, config)
