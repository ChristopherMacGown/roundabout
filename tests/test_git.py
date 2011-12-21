import os
import git
import time
import unittest

from roundabout.config import Config
from roundabout.git_client import Git, GitException
from tests import utils


def create_test_repo():
    repo_path = utils.testdata('test_repo')
    if not os.path.exists(repo_path):
        repo = git.Repo.init(repo_path, mkdir=True)
        with open(os.path.join(repo_path, "README"), "w") as fp:
            fp.write("This is just test stuff")
        repo.git.execute(("git", "add", "README"))
        repo.git.execute(("git", "commit", "-m", "Test commit"))
    return repo_path


class GitTestCase(utils.TestHelper):
    def setUp(self):
        self.t = time.time()

        repo_path = create_test_repo()
        config = Config(config_file=utils.testdata('good_git.cfg'))
        config["git"]["base_repo_url"] = repo_path

        remote_branch = config["test"]["remote_branch"]
        remote_name = config["test"]["remote_name"]
        remote_url = repo_path

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

    def test_clean_squash_merge_with_good_Config(self):
        branch = self.repo.remote_branch
        self.repo.repo.create_head(branch)
        self.repo.branch(branch).checkout()

        curdir = os.getcwd()
        os.chdir(self.repo.clonepath)

        with open("testfile", "w") as test:
            test.write("this is just a test")
        
        self.repo.repo.git.execute(('git', 'add', 'testfile'))
        self.repo.repo.git.execute(("git", "commit", "-m", "test_commit"))
        self.repo.branch("master").checkout()
        self.assertTrue(self.repo.merge(branch, squash=True))
        os.chdir(curdir)

    def test_clean_squash_merge_with_good_config_but_no_squash_message(self):
        branch = self.repo.remote_branch
        self.repo.repo.create_head(branch)
        self.repo.branch(branch).checkout()

        curdir = os.getcwd()
        os.chdir(self.repo.clonepath)

        with open("testfile", "w") as test:
            test.write("this is just a test")
        
        self.repo.repo.git.execute(('git', 'add', 'testfile'))
        self.repo.repo.git.execute(("git", "commit", "-m", "test_commit"))
        self.repo.branch("master").checkout()
        self.repo.clonepath="/i/am/a/fake/path/"
        self.assertTrue(self.repo.merge(branch, squash=True))
        os.chdir(curdir)

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
        self.assertTrue(self.repo.push('master', remote_branch='foo'))

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
        remote_name = config["test"]["remote_name"]
        remote_url = config["test"]["remote_url"]
        remote_branch = config["test"]["remote_branch"]

        self.assertRaises(GitException, Git, remote_name, remote_url, remote_branch, config)
