import git
import time
import unittest

from roundabout.config import Config
from roundabout.git_client import Git, GitException
from tests import utils


class GitTestCase(utils.TestHelper):
    def setUp(self):
        self.t = time.time()
        config = Config(config_file=utils.testdata('good_git.cfg'))
        remote_name = config.test_remote_name
        remote_url = config.test_remote_url
        remote_branch = config.test_remote_branch
        self.repo = Git(remote_name=remote_name,
                        remote_url=remote_url,
                        remote_branch=remote_branch,
                        config=config)

    def tearDown(self):
        print "%s: %f" % (self.id(), time.time() - self.t)

    def test_clone_repo_with_good_config(self):
        self.assertTrue(self.repo)

    def test_enter_repo_with_good_config(self):
        self.repo.repo.create_head(self.repo.remote_branch)
        self.assertTrue(self.repo.__enter__())
        self.assertTrue(self.repo.branch('master').checkout())
        self.assertFalse(self.repo.__exit__())

    def test_clean_merge_with_good_config(self):
        self.repo.repo.create_head(self.repo.remote_branch)

        with self.repo as repo:
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

        self.repo.repo.create_head(self.repo.remote_branch)
        self.repo.repo.git = FakeGit()

        self.assertRaises(GitException, self.repo.merge, "master")
        try:
            self.assertCalled(self.repo.repo.git.reset, self.repo.merge, "master")
        except GitException, e:
            pass

    def test_push_with_good_config(self):
        self.assertTrue(self.repo.push('master'))

    def test_cleanup_master_raises(self):
        self.repo.local_branch_name = 'master'
        self.assertRaises(GitException, self.repo.cleanup)

    def test_cleanup_with_os_error_raises(self):
        self.repo.clonepath = "/this/path/doesn't/exist"
        self.assertRaises(GitException, self.repo.cleanup)

    def test_cleanup_with_good_config_doesnt_raise(self):
        try:
            self.repo.cleanup()
        except GitException, e:
            result = False
        else:
            result = True

        self.assertTrue(result)

    def test_clone_repo_with_bad_config(self):
        config = Config(config_file=utils.testdata('bad_git.cfg'))
        remote_name = config.test_remote_name
        remote_url = config.test_remote_url
        remote_branch = config.test_remote_branch

        self.assertRaises(GitException, Git, remote_name, remote_url, remote_branch, config)
