""" The Roundabout git package """

from __future__ import absolute_import
import git
import os
import random
import string
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
        self.config = config

        clonename = "".join([random.choice(string.letters) for i in range(8)])
        clonepath = os.path.join(config.git_local_repo_path, clonename)
        try:
            self.repo = git.Repo.clone_from(config.git_base_repo_url, clonepath)
        except git.GitCommandError, e:
            raise GitException(e)

    def __enter__(self):
        self.repo.create_remote(self.remote_name, self.remote_url)
        self.repo.create_head(self.local_branch_name)
        self.branch(self.local_branch_name).checkout()
        return self

    def __exit__(self, *args):
        self.repo.delete_remote(self.remote_name)
        self.repo.delete_head(self.local_branch_name)

    def branch(self, branch):
        """ Return the head object referenced by the branch name """
        return [b for b in self.repo.branches if branch == b.name][0]

    def merge(self, branch):
        """ Merge the passed in branch with HEAD """
        return self.repo.git.execute(('git', 'merge', branch))

    def push(self, branch, remote='origin'):
        """ Push the branch up to the remote """
        self.repo.remote(remote).push(branch)
