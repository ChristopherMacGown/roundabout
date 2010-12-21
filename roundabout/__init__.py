""" Roundabout is a tarmac style merge bot for github """

import sys
import time
from roundabout.git import Git
from roundabout.github.client import Client
from roundabout.hudson import Hudson


class Roundabout(object):
    """ Tarmac style merge bot for github """

    @classmethod
    def run(cls):
        """ Daemonize and poll for good pull requests """
        while True:
            github = Client()
            if not github.pull_requests: # Check for approved pull requests
                print "CONTINUING"
                continue

            pull_requests = [(u, p) for u, p
                                    in github.pull_requests.items()
                                    if p.lgtm(github.approvers)]

            for url, pull_request in pull_requests:
                print "processing pull_request (%s)" % url

                # TODO(chris): Eventletify this so that pull_requests are 
                # processed asynchronously. 
                repo = Git(remote_name=pull_request.remote_name,
                           remote_url=pull_request.remote_url,
                           remote_branch=pull_request.remote_branch)

                # Create a remote, fetch it, checkout the branch
                with repo as git:
                    try:
                        git.merge('master')
                    except git.exc.GitCommandError:
                        # TODO(chris): Log here and continue. 
                        raise

                    git.push(git.local_branch_name)
                    hudson_result = Hudson.spawn_job(git.local_branch_name)
                    while not hudson_result.complete:
                        time.sleep(30)

                    # return to master
                    git.branch('master').checkout()

                    if hudson_result: 
                        # Successful build, good coverage, and clean pylint.
                        git.merge(git.local_branch_name)
                        git.push('master')

                    # reject
            sys.exit(0)
