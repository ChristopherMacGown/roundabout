""" Roundabout is a tarmac style merge bot for github """

import sys
import time

import roundabout.config
import roundabout.daemon
import roundabout.github.client

from roundabout import log
from roundabout import git_client
from roundabout import pylint
from roundabout import hudson


def main(command, options):
    """ Function called by bin/roundabout """

    config_file = options.config_file or roundabout.config.DEFAULT
    config = roundabout.config.Config(config_file)
    if command == "run": 
        log.init_logger(config, stream=True)
    else:
        log.init_logger(config)

        daemon = roundabout.daemon.Daemon(
                    stdin="roundabout.log",
                    stdout="roundabout.log",
                    stderr="roundabout.log",
                    pidfile=config.default_pidfile or "roundabout.pid")

        if command == "start":
            daemon.start()
        elif command == "stop":
            daemon.stop()
            sys.exit(0)
        elif command == "restart":
            daemon.restart()

    try:
        run(config)
    except KeyboardInterrupt:
        sys.exit(0)

def run(config):
    """ 
    Run roundabout forever or until you kill it.
    """

    while True:
        github = roundabout.github.client.Client(config)

        try:
            pull_requests = github.pull_requests
            pull_requests = [(u, p) for u, p
                                    in pull_requests.items()
                                    if p.lgtm(github.approvers)]
        except RuntimeError, e:
            log.error("Unexpected response from github:\n %s" % e.__str__())
            pull_requests = []

        if not pull_requests:
            log.info("No work to do, sleeping.")
            time.sleep(30)
            continue

        for url, pull_request in pull_requests:
            log.info("processing %s" % url)

            repo = git_client.Git(remote_name=pull_request.remote_name,
                                  remote_url=pull_request.remote_url,
                                  remote_branch=pull_request.remote_branch,
                                  config=config)

            # Create a remote, fetch it, checkout the branch

            with repo as git:
                log.info("Cloning to %s" % repo.clonepath)

                # Ensure we're on master
                git.branch("master").checkout()
                try:
                    git.merge(git.remote_branch,
                              squash=config.git_squash_merges)
                except git_client.GitException, e:
                    pull_request.close(git_client.MERGE_FAIL_MSG % e)
                    continue

                if config.pylint_modules:
                    py_res = pylint.Pylint(config.pylint_modules,
                                           config=config, path=repo.clonepath)
                    if not py_res:
                        pull_request.close(pylint.PYLINT_FAIL_MSG %
                        (py_res.previous_score, config.pylint_current_score))
                        continue

                # push up a test branch
                git.push("master", remote_branch=git.local_branch_name)

                build = hudson.Job.spawn_build(git.local_branch_name, config)
                while not build.complete:
                    log.info("Job not complete, sleeping for 30 seconds...")
                    time.sleep(30)
                    build.reload()

                if build:
                    # Successful build, good coverage, and clean pylint.
                    git.push("master")
                    pull_request.close(git_client.BUILD_SUCCESS_MSG)
                else:
                    pull_request.close(
                        git_client.BUILD_FAIL_MSG % build.url)
