""" The Roundabout git package """

from __future__ import absolute_import
import git
import os
import random
import string
from roundabout import log
from roundabout.config import Config


class GitException(Exception):
    """ """
    pass


class Git(object):
    """ Roundabout git package proxy """ 

    def __init__(self, remote_name, remote_url, remote_branch, config=Config()):
        self.remote_name = remote_name
        self.remote_url = remote_url
        self.local_branch_name = "merge_%s" % remote_branch
        self.remote_branch = "remotes/%s/%s" % (remote_name, remote_branch)
        self.config = config

        clonename = "".join([random.choice(string.letters) for i in range(8)])
        self.clonepath = os.path.join(config.git_local_repo_path, clonename)
        try:
            self.repo = git.Repo.clone_from(config.git_base_repo_url,
                                            self.clonepath)
        except git.GitCommandError, e:
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
        return self.repo.git.execute(('git', 'merge', branch))

    def push(self, branch, remote='origin'):
        """ Push the branch up to the remote """
        log.info("pushing %s to %s" % (branch, remote))
        return self.repo.remote(remote).push(branch)
