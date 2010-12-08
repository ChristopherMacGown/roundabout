""" A borg style github client """

from __future__ import absolute_import
from github2.client import Github
from roundabout.config import Config
from roundabout.github.scraper import GithubScraper, parse_pull_requests


class Client(object):
    """ A borg style github client """
    __shared_state = {}

    def __new__(cls, config=Config()): #pylint: disable=W0613
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
        """ return the list of issues from the repo """
        return self.github.issues.list(self.config.github_repo)

    @property
    def branches(self):
        """ Return the list of branches from the repo """
        return self.github.repos.branches(self.config.github_repo)

    @property
    def pull_requests(self):
        """ Use the scraper to grab any pull requests and their commit hashes. 
        """
        url = "https://github.com/%s/pulls" % self.config.github_repo
        with GithubScraper(url) as response: 
            return [pull_request 
                    for pull_requests 
                    in parse_pull_requests(response.read())
                    if LGTM_RE.match(pull_request['comment_text'])]
