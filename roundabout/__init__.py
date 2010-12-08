""" Roundabout is a tarmac style merge bot for github """

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
                continue

            for pull_request in github.pull_requests:
                repo = Git(remote_name=pull_request['remote_name'],
                           remote_url=pull_request['remote_url'],
                           remote_branch=pull_request['remote_branch'])

                with repo as git:
                    try:
                        git.repo.git.execute(('git', 'merge', 'master')) # Merge in master
                    except git.exc.GitCommandError, e:
                        raise

                    git.repo.remote('origin').push(git.local_branch_name)
                    hudson_result = Hudson.spawn_job(git.local_branch_name)
                    while not hudson_result.complete:
                        sleep(30)

                    if hudson_result: # Successful build, good coverage, and clean pylint.
                        for branch in git.repo.branches:
                            if branch.name == 'master':
                                branch.checkout()
                                break

                        git.repo.git.execute(('git', 'merge', git.local_branch_name))
                        git.remote('origin').push()

                    # reject
