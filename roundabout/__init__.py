""" Roundabout is a tarmac style merge bot for github """

import sys
import time
from roundabout import log
from roundabout.git import Git
from roundabout.github.client import Client
from roundabout.hudson import Job


class Roundabout(object):
    """ Tarmac style merge bot for github """

    @classmethod
    def run(cls):
        """ Daemonize and poll for good pull requests """
        while True:
            log.info("Daemonizing")
            github = Client()
            pull_requests = github.pull_requests

            pull_requests = [(u, p) for u, p
                                    in pull_requests.items()
                                    if p['lgtm'](github.approvers)]

            if not pull_requests:
                log.info("No work to do, sleeping.")
                time.sleep(30)

            for url, pull_request in pull_requests:
                log.info("processing %s" % url)
                repo = Git(remote_name=pull_request.remote_name,
                           remote_url=pull_request.remote_url,
                           remote_branch=pull_request.remote_branch)

                # Create a remote, fetch it, checkout the branch
                with repo as git:
                    try:
                        log.info("merging master into remote")
                        git.merge('master')
                    except git.exc.GitCommandError:
                        # TODO(chris): Log here and continue. 
                        raise

                    log.info("Starting hudson job")
                    git.push(git.local_branch_name)
                    build = Job.spawn_build(git.local_branch_name)
                    while not build.complete:
                        log.info("Job not complete, sleeping for 30 seconds...")
                        time.sleep(30)
                        build.reload()

                    # return to master
                    git.branch('master').checkout()

                    if build:
                        log.info("Build successful, merging %s into master" % url)
                        # Successful build, good coverage, and clean pylint.
                        git.merge(git.local_branch_name)
                        git.push('master')
                    else:
                        log.info("Build failed, rejecting %s" % url)

            sys.exit(0)
