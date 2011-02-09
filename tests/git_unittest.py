import git
import time
import unittest

from roundabout.config import Config
from roundabout.git_client import Git, GitException
from tests import utils


class GitTestCase(utils.TestHelper):
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

        repo = Git(remote_name=remote_name,
                   remote_url=remote_url,
                   remote_branch=remote_branch)
        repo.repo.create_head(repo.remote_branch)
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
        repo.repo.create_head(repo.remote_branch)

        with repo as repo:
            self.assertTrue(repo.merge('master'))
            self.assertTrue(repo.branch('master').checkout())

    def test_merge_fails_for_some_reason_should_raise(self):
        class FakeGit(git.Repo):
            """ A fake git class """
            def execute(self, command):
                """ No matter what, we raise a git.exc.GitCommandError """
                raise git.exc.GitCommandError(command, -9999)

            def reset(self, *args, **kwargs):
                """ Pretend to reset a failed merge. """
                pass


        config = Config(config_files=[utils.testdata('good_git.cfg')])
        remote_name = config.git_test_remote_name
        remote_url = config.git_test_remote_url
        remote_branch = config.git_test_remote_branch

        repo = Git(remote_name=remote_name,
                  remote_url=remote_url,
                  remote_branch=remote_branch)
        repo.repo.create_head(repo.remote_branch)
        repo.repo.git = FakeGit()

        self.assertRaises(GitException, repo.merge, "master")
        try:
            self.assertCalled(repo.repo.git.reset, repo.merge, "master")
        except GitException, e:
            pass

    def test_push_with_good_config(self):
        config = Config(config_files=[utils.testdata('good_git.cfg')])
        remote_name = config.git_test_remote_name
        remote_url = config.git_test_remote_url
        remote_branch = config.git_test_remote_branch

        repo = Git(remote_name=remote_name,
                   remote_url=remote_url,
                   remote_branch=remote_branch)

        self.assertTrue(repo.push('master'))

    def test_cleanup_master_raises(self):
        config = Config(config_files=[utils.testdata('good_git.cfg')])
        remote_name = config.git_test_remote_name
        remote_url = config.git_test_remote_url
        remote_branch = config.git_test_remote_branch

        repo = Git(remote_name=remote_name,
                   remote_url=remote_url,
                   remote_branch=remote_branch)
        repo.local_branch_name = 'master'

        self.assertRaises(GitException, repo.cleanup)

    def test_cleanup_with_os_error_raises(self):
        config = Config(config_files=[utils.testdata('good_git.cfg')])
        remote_name = config.git_test_remote_name
        remote_url = config.git_test_remote_url
        remote_branch = config.git_test_remote_branch

        repo = Git(remote_name=remote_name,
                   remote_url=remote_url,
                   remote_branch=remote_branch)

        repo.clonepath = "/this/path/doesn't/exist"

        self.assertRaises(GitException, repo.cleanup)

    def test_cleanup_with_good_config_doesnt_raise(self):
        config = Config(config_files=[utils.testdata('good_git.cfg')])
        remote_name = config.git_test_remote_name
        remote_url = config.git_test_remote_url
        remote_branch = config.git_test_remote_branch

        repo = Git(remote_name=remote_name,
                   remote_url=remote_url,
                   remote_branch=remote_branch)

        try:
            repo.cleanup()
        except GitException, e:
            result = False
        else:
            result = True

        self.assertTrue(result)

    def test_clone_repo_with_bad_config(self):
        config = Config(config_files=[utils.testdata('bad_git.cfg')])
        remote_name = config.git_test_remote_name
        remote_url = config.git_test_remote_url
        remote_branch = config.git_test_remote_branch

        self.assertRaises(GitException, Git, remote_name, remote_url, remote_branch, config)
