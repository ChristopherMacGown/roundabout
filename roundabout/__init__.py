""" Roundabout is a tarmac style merge bot for github """

import sys
import time

import roundabout.config
import roundabout.daemon
import roundabout.github.client

from roundabout import log
from roundabout import git_client
from roundabout import pylint
from roundabout import ci


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
                    pidfile=config["default"].get("pidfile", "roundabout.pid"))

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
        pass
    except Exception, e:
        log.error("Unknown error: %s" % str(e))
    finally:
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
            log.error("Unexpected response from github:\n %s" % str(e))
            pull_requests = []

        if not pull_requests:
            log.info("No work to do, sleeping.")
            # todo(chris): Make this configurable.
            # config["default"]["no_work_time"] or something
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

                # Ensure we're on the requested branch for the pull_request.

                base_branch = pull_request.base_branch
                git.branch(base_branch).checkout()
                try:
                    git.merge(git.remote_branch,
                              squash=config["git"].get("squash_merges"))
                except git_client.GitException, e:
                    pull_request.close(git_client.MERGE_FAIL_MSG % e)
                    continue

                if config["pylint"]:
                    py_res = pylint.Pylint(config["pylint"]["modules"],
                                           config=config, path=repo.clonepath)
                    if not py_res:
                        pull_request.close(
                            pylint.PYLINT_FAIL_MSG % (py_res.previous_score,
                                                      py_res.current_score))
                        continue

                # push up a test branch
                git.push(base_branch, remote_branch=git.local_branch_name)

                with ci.job.Job.spawn(git.local_branch_name, config) as job:
                    while not job.complete:
                        job.reload()

                    if job:
                        # Successful build, good coverage, and clean pylint.
                        git.push(base_branch)
                        pull_request.close(git_client.BUILD_SUCCESS_MSG)
                    else:
                        pull_request.close(git_client.BUILD_FAIL_MSG % job.url)
