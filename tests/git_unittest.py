import unittest
from roundabout.config import Config
from roundabout.git import Git, GitException
from tests import utils

class GitTestCase(unittest.TestCase):
    def setUp(self):
        utils.reset_config()

    def tearDown(self):
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

        repo = Git(remote_name=remote_name,
                   remote_url=remote_url,
                   remote_branch=remote_branch)

        self.assertTrue(repo.__enter__())
        self.assertTrue(repo.branch('master').checkout())
        self.assertFalse(repo.__exit__())

    def test_clean_merge_with_good_config(self):
        config = Config(config_files=[utils.testdata('good_git.cfg')])
        remote_name = config.git_test_remote_name
        remote_url = config.git_test_remote_url
        remote_branch = config.git_test_remote_branch

        repo = Git(remote_name=remote_name,
                   remote_url=remote_url,
                   remote_branch=remote_branch)

        with repo as git:
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
