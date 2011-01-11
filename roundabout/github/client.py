""" A borg style github client """

from __future__ import absolute_import
import re
from github2.client import Github
from roundabout import log
from roundabout.config import Config

LGTM_RE = re.compile("^%s$" % Config().default_lgtm)

class Client(object):
    """ A borg style github client """
    __shared_state = {}

    def __new__(cls, config=Config(), conn_class=Github): #pylint: disable=W0613
        self = object.__new__(cls)
        self.__dict__ = cls.__shared_state
        return self

    def __init__(self, config=Config(), conn_class=Github):
        self.config = config
        self.github = conn_class(username=config.github_username,
                             api_token=config.github_api_token,
                             requests_per_second=config.github_req_per_second)

    def _get(self, *args):
        return self.github.request.get(*args)

    @property
    def approvers(self):
        core_team = self.config.github_core_team
        try:
            return [user['login'] for user in self.teams[core_team]['users']]
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
        p_reqs = [PullRequest(self, p)
                  for p
                  in self._get("pulls", self.config.github_repo)['pulls']]
        return dict([(p.html_url, p) for p in p_reqs])


class PullRequest(object):
    """ A github pull request """
    def __init__(self, client, pull_request):
        """ Take a pull_request dict from github, and builds a PullRequest """

        self.__dict__ = pull_request
        self.client = client

        self.__dict__.update(self.__get_full_request())

    @property
    def remote_url(self):
        return self.head['repository']['url'] + ".git"

    @property
    def remote_name(self):
        return self.head['repository']['owner']

    @property
    def remote_branch(self):
        return self.head['ref']

    def lgtm(self, approvers):
        """ Takes a list of approvers and checks if any of the approvers have
            "lgtmed" the request. Returns true if so, None otherwise. """

        for comment in self.discussion:
            if comment['user']['login'] in approvers and LGTM_RE.match(comment.get('body', "")):
                return True


    def __get_full_request(self):
        """ Return a dict of the complete pull_request data from the github api
            for a single pull_request. """

        print self.client
        return self.client._get("pulls",
                                self.client.config.github_repo,
                                str(self.number))['pull']

    def comment(self, issue_id, message):
        """
        Add a comment to the specified issue.

        Returns a dict representation of the comment.
        """
        log.info("commenting on %s: %s" % (issue_id, message))
        return self.client.github.issues.comment(self.client.config.github_repo,
                                                 issue_id, message)

    def reject(self, pull_request_id, message):
        """
        Add a rejection reason (comment) to the specified pull request,
        then close it.

        Returns the closed Issue.
        """

        log.info("Rejecting %s" % self.html_url)
        self.comment(pull_request_id, message)
        return self.client.github.issues.close(self.client.config.github_repo,
                                               pull_request_id)
