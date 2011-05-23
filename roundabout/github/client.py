""" A borg style github client """

from __future__ import absolute_import
import re
from github2.client import Github
from roundabout import log

class Client(object):
    """ A borg style github client """
    __shared_state = {}

    def __new__(cls, config, conn_class=Github): #pylint: disable=W0613
        self = object.__new__(cls)
        self.__dict__ = cls.__shared_state
        return self

    def __init__(self, config, conn_class=Github):
        self.config = config
        self.github = conn_class(
            username=config["github"]["username"],
            api_token=config["github"]["api_token"],
            requests_per_second=config["github"]["req_per_second"]
        )
        self.organization = self.config["github"]["organization"]

    def get(self, *args):
        """ Return a github request built from the *args """
        return self.github.request.get(*args)

    @property
    def approvers(self):
        """
        Return a list of usernames permitted to approve a merge request
        """

        core_team = self.config["github"]["core_team"]
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
        teams = self.get('organizations', self.organization, "teams")['teams']

        for team in teams:
            team.update(self.get("teams", str(team['id']), "members"))
            teams_with_members[team['name']] = team
        return teams_with_members

    @property
    def issues(self):
        """ return the list of issues from the repo """
        return self.github.issues.list(self.config["github"]["repo"])

    @property
    def branches(self):
        """ Return the list of branches from the repo """
        return self.github.repos.branches(self.config["github"]["repo"])

    @property
    def pull_requests(self):
        """ Return the list of pull_requests from the repo. """
        p_reqs = [PullRequest(self, p, self.config["default"]["lgtm"])
                  for p
                  in self.get("pulls", self.config["github"]["repo"])['pulls']]
        return dict([(p.html_url, p) for p in p_reqs])


class PullRequest(object):
    #pylint: disable=E1101
    """ A github pull request """

    def __init__(self, client, pull_request, lgtm_text):
        """ Take a pull_request dict from github, and builds a PullRequest """

        self.__dict__ = pull_request
        self.client = client
        self.lgtm_text = lgtm_text

        self.__dict__.update(self.__get_full_request())

    @property
    def remote_url(self):
        """ Return the remote URL from the repository dict. """
        return self.head['repository']['url'] + ".git"

    @property
    def remote_name(self):
        """Return the login of the branch owner."""
        return self.head['repository']['owner']

    @property
    def remote_branch(self):
        """Return the branch name for the requested merge branch."""
        return self.head['ref']

    @property
    def base_branch(self):
        """Return the base branch name for the requested merge branch."""
        return self.base["ref"]

    def lgtm(self, approvers):
        """ 
        Takes a list of approvers and checks if any of the approvers have
        "lgtmed" the request. Returns true if so, None otherwise.
        """

        lgtm_re = re.compile("^%s$" % self.lgtm_text, re.I)
        rejected_re = re.compile("rejecting")


        lgtms = []
        rejected = [c for c
                      in self.discussion
                      if rejected_re.search(c.get('body', ''))]

        for comment in self.discussion:
            try:
                if comment['user']['login'] in approvers and \
                   lgtm_re.match(comment.get('body', "")):
                    lgtms.append(comment)
            except TypeError:
                continue

        return len(rejected) < len(lgtms)

    def __get_full_request(self):
        """
        Return a dict of the complete pull_request data from the github api
        for a single pull_request.
        """

        return self.client.get("pulls",
                               self.client.config["github"]["repo"],
                               str(self.number))['pull']

    def comment(self, message):
        """
        Add a comment to the specified issue.

        Returns a dict representation of the comment.
        """
        log.info("commenting on %s: %s" % (self.number,  message))
        return self.client.github.issues.comment(
                    self.client.config["github"]["repo"], self.number, message)

    def close(self, message):
        """
        Add a comment to this pull request and close it.

        Returns the closed Issue.
        """

        self.comment(message)
        log.info("Closing %s" % self.html_url)
        return self.client.github.issues.close(
                self.client.config["github"]["repo"], self.number)
