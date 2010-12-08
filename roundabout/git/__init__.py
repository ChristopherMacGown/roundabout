""" The Roundabout git package """

from __future__ import absolute_import
import git
from roundabout.config import Config

class Git(object):
    """ Roundabout git package proxy """ 

    def __init__(self, remote_name, remote_url, remote_branch, config=Config()):
        self.remote_name = remote_name
        self.remote_url = remote_url
        self.local_branch_name = "merge_%s" % remote_branch
        self.repo = git.Repo(config.git_local_repo_path)

    def __enter__(self):
        self.repo.create_remote(self.remote_name, self.remote_url)
        self.repo.create_head(self.local_branch_name)
        self.repo.head(self.local_branch_name)
        return self

    def __exit__(self):
        self.repo.delete_remote(self.remote_name)
        self.repo.delete_head(self.local_branch_name)


