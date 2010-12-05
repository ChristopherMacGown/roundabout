""" A borg style github client """

from __future__ import absolute_import
from github2.client import Github
from roundabout.config import Config

class Client(object):
    """ A borg style github client """
    __shared_state = {}

    def __new__(cls, config=Config()):
        self = object.__new__(cls)
        self.__dict__ = cls.__shared_state
        return self

    def __init__(self, config=Config()):
        self.config = config
        self.github = Github(username=config.github_username,
                             api_token=config.github_api_token,
                             requests_per_second=config.github_req_per_second)

    @property
    def issues(self):
        return self.github.issues.list(self.config.github_repo)

    @property
    def branches(self):
        return self.github.repos.branches(self.config.github_repo)
