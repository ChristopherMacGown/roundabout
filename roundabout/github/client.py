""" A borg style github client """

from __future__ import absolute_import
import re
from github2.client import Github
from roundabout.config import Config

LGTM_RE = re.compile("^%s$" % Config().default_lgtm)

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

    def _get(self, *args):
        return self.github.request.get(*args)

    def comment(self, issue_id, comment):
        "Add a comment to the specified issue id"
        return self.github.issues.comment(self.config.github_repo,
                                                 issue_id,
                                                 comment)
    
    def get_full_pull_request(self, pull_request):
        def lgtm(pull_request, approvers):
            def _lgtm(approvers):
                for c in pull_request.discussion:
                    if c['user']['login'] in approvers and LGTM_RE.match(c['body']):
                        return True
            return _lgtm

        pull_request = self.github.pull_requests.show(self.config.github_repo, pull_request.number)
        pull_request.lgtm = lgtm(pull_request, self.approvers)
        return pull_request

    @property
    def approvers(self):
        core_team = self.config.github_core_team
        try:
            return [user['name'] for user in self.teams[core_team]['users']]
        except KeyError:
            return []

    @property
    def teams(self):
        """ Queries github for an organization's teams and returns a dict with
        the team and its members
        """
        teams_with_members = {}
        teams = self._get('organizations', self.organization, "teams")['teams']

        for team in teams:
            team.update(self._get("teams", str(team['id']), "members"))
            teams_with_members[team['name']] = team
        return teams_with_members

    @property
    def organization(self):
        return self.config.github_organization

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
        """ Return the list of pull_requests from the repo. """
        return [self.get_full_pull_request(p) for p in 
                self.github.pull_requests.list(self.config.github_repo)]
