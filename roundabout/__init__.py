""" Roundabout is a tarmac style merge bot for github """

import sys
import time
from roundabout import log
from roundabout import git_client
from roundabout.github.client import Client
from roundabout.hudson import Job


class Roundabout(object):
    """ Tarmac style merge bot for github """

    @classmethod
    def run(cls):
        """ Daemonize and poll for good pull requests """
        log.info("Daemonizing")

        while True:
            github = Client()
            pull_requests = github.pull_requests
            pull_requests = [(u, p) for u, p
                                    in pull_requests.items()
                                    if p.lgtm(github.approvers)]

            if not pull_requests:
                log.info("No work to do, sleeping.")
                time.sleep(30)

            for url, pull_request in pull_requests:
                log.info("processing %s" % url)

                repo = git_client.Git(remote_name=pull_request.remote_name,
                                      remote_url=pull_request.remote_url,
                                      remote_branch=pull_request.remote_branch)

                # Create a remote, fetch it, checkout the branch

                with repo as git:
                    log.info("Cloning to %s" % repo.clonepath)
                    try:
                        git.merge('master')
                    except git_client.GitException, e:
                        pull_request.close(git_client.MERGE_FAIL_MSG % e)
                        continue

                    git.push(git.local_branch_name)
                    build = Job.spawn_build(git.local_branch_name)
                    while not build.complete:
                        log.info("Job not complete, sleeping for 30 seconds...")
                        time.sleep(30)
                        build.reload()

                    # return to master
                    git.branch('master').checkout()

                    if build:
                        # Successful build, good coverage, and clean pylint.
                        git.merge(git.local_branch_name)
                        git.push('master')
                        pull_request.close(git_client.BUILD_SUCCESS_MSG)
                    else:
                        pull_request.close(git_client.BUILD_FAIL_MSG % build.url)
