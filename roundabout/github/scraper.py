""" A screen scraper for github pull requests since they don't exist in 
the API yet. """

import cookielib
import lxml.html
import re
import urllib
import urllib2

from roundabout.config import Config

GITHUB_BASE_HREF = "https://github.com"
PULL_REQUEST_RE = re.compile("%s(.*)/pull/\d+" % GITHUB_BASE_HREF)
COMMIT_RE = re.compile("%s(.*)/commit/(.*)" % GITHUB_BASE_HREF)
LGTM_RE = re.compile("^%s$" % Config().default_lgtm)


class PullRequest(object):
    """ A single pull request """
    def __init__(self, commits, comments, remote_name, remote_branch, remote_url):
        self.commits = commits 
        self.comments = comments
        self.remote_name = remote_name
        self.remote_branch = remote_branch
        self.remote_url = remote_url

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def lgtm(self, approvers):
        return True
        for c in self.comments:
            if c['author'] in approvers and LGTM_RE.match(c['body']):
                return True

def parse_pull_requests(html):
    """ Scrape the pull requests page for requests and then build a list
    of github commit URLs from them. Perhaps we only need the SHA??
    """

    doc = lxml.html.document_fromstring(html)
    doc.make_links_absolute(GITHUB_BASE_HREF)
    listings = doc.find_class('listings')[0]
    requests = {}

    for listing in listings:
        for child in listing.getchildren():
            for link in child.iterlinks():
                path = link[2] # (element, 'href', path, position)
                if PULL_REQUEST_RE.match(path) and not requests.get(path, None):
                    with GithubScraper(path) as res: 
                        requests[path] = parse_pull_request_page(res.read())
    return requests


def parse_pull_request_page(html):
    """ Parse the pull request page, returning a list of URLs to the commits """
    doc = lxml.html.document_fromstring(html)
    doc.make_links_absolute(GITHUB_BASE_HREF)
    commits = __parse_commits(doc.find_class('commits')[0])
    comments = __parse_comments(doc.find_class('comments-wrapper')[0])
    remote_name, remote_branch = __parse_pull_desc(doc.find_class('pull-description')[0])
    remote_url = __parse_remote_url(doc.find_class('help-steps')[0])
    return PullRequest(commits, comments, remote_name, remote_branch, remote_url)

def __parse_commits(commits):    
    commit_hashes = []

    for commit in commits:
        for link in commit.iterlinks():
            path = link[2] # (element, 'href', path, position)
            sha1 = (COMMIT_RE.match(path) and COMMIT_RE.sub(r'\2', path))
            if sha1 and not sha1 in commit_hashes:
                commit_hashes.append(sha1)

    return commit_hashes

def __parse_comments(comments_wrapper):
    comments = []
    for comment in comments_wrapper.find_class("comment normal-comment"):
        cmeta_author = comment.find_class("cmeta")[0].find_class("author")[0]
        cbody = comment.find_class("body")[0]
        author = cmeta_author.find("strong").text_content()
        body = cbody.find_class("content-body")[0].text_content().strip()
        comments.append({'author': author, 'body': body})

    return comments

def __parse_pull_desc(desc):
    cr_from = desc.find_class('commit-ref from')[0].text_content()
    return cr_from.split(':')
    
def __parse_remote_url(help_steps):
    ct = help_steps.find_class('copyable-terminal')[1]
    return ct.text_content().split()[2]

class GithubScraper(object): #pylint: disable=R0903
    
    """ A class that wraps urllib2 and cookielib to provide 
    __enter__/__exit__ """



    def __init__(self, url, config=Config()):
        self.config = config
        self.cookie_jar, self.opener = self._load_cookie_handler()
        self.url = url
        self.res = None

    def __enter__(self):
        self.res = self.opener.open(self.url)
        if not self.res.geturl() == self.url:
            self._login()
            self.res = self.opener.open(self.url)

        return self.res

    def __exit__(self, *args):
        self.res.close()

    def _login_authenticity_token(self):
        """ Parse the login page and return the authenticity_token """
        doc = lxml.html.document_fromstring(self.res.read())
        form = doc.forms[0]
        return form.fields['authenticity_token']

    def _login(self):
        """ Log into github """
        session_url = "https://github.com/session"
        auth_token = self._login_authenticity_token()
        credentials = urllib.urlencode({'login': self.config.github_username,
                                        'password': self.config.github_passwd,
                                        'authenticity_token': auth_token,
                                        'commit': 'Log in'})

        res = self.opener.open(session_url, credentials)
        self.cookie_jar.save(self.config.default_cookie_file)
        res.close()

    def _load_cookie_handler(self):
        """ Load the cookie jar into the urllib2 opener """
        cookie_jar = cookielib.LWPCookieJar()
        try:
            cookie_jar.load(self.config.default_cookie_file)
        except IOError:
            cookie_jar.save(self.config.default_cookie_file)
            cookie_jar.load(self.config.default_cookie_file)

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
        urllib2.install_opener(opener)

        return cookie_jar, opener
