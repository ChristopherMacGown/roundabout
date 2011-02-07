""" The Roundabout git module. """

import git
import os

from git import Repo, GitCommandError #pylint: disable=E1101
from random import choice
from string import letters #pylint: disable=W0402

from roundabout import log
from roundabout.config import Config


class GitException(BaseException):
    """ Roundabout git exceptions """
    def __init__(self, exc):
        super(GitException, self).__init__(exc)
        log.error(str(exc))

class Git(object):
    """ Roundabout git package proxy """ 

    def __init__(self, remote_name, remote_url, remote_branch, config=Config()):
        self.remote_name = remote_name
        self.remote_url = remote_url
        self.local_branch_name = "merge_%s" % remote_branch
        self.remote_branch = "remotes/%s/%s" % (remote_name, remote_branch)
        self.config = config

        cn = "".join([choice(letters) for i in range(8)]) #pylint: disable=W0612
        self.clonepath = os.path.join(config.git_local_repo_path, cn)
        try:
            self.repo = Repo.clone_from(config.git_base_repo_url,
                                            self.clonepath)
        except GitCommandError, e:
            raise GitException(e)

    def __enter__(self):
        self.remote.fetch()
        self.repo.git.checkout(self.remote_branch, b=self.local_branch_name)
        return self

    def __exit__(self, *args):
        self.repo.delete_remote(self.remote_name)
        self.repo.delete_head(self.local_branch_name)

    @property
    def remote(self):
        """ Create and return the remote object """
        self.repo.create_remote(self.remote_name, self.remote_url)
        return [remote for remote
                       in self.repo.remotes
                       if remote.name == self.remote_name][0]

    def branch(self, branch):
        """ Return the head object referenced by the branch name """
        return [b for b in self.repo.branches if branch == b.name][0]

    def merge(self, branch):
        """ Merge the passed in branch with HEAD """

        log.info("merging %s into %s" % (branch, self.repo.active_branch.name))
        try:
            return self.repo.git.execute(('git', 'merge', branch))
        except git.exc.GitCommandError, e:
            raise GitException(e)

    def push(self, branch, remote='origin'):
        """ Push the branch up to the remote """
        log.info("pushing %s to %s" % (branch, remote))
        return self.repo.remote(remote).push(branch)


