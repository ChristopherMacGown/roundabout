Summary:
==================

Roundabout is a tool that automatically prevents code with failing tests from
being merged into a github repository. It uses github's pull request API to grab
approved branches, creates CI jobs for the merge, and if either the CI job or
the git merge fails rejects the merge. Roundabout also supports pylint checking,
which means a project can programatically enforce code quality in merges.

Currently roundabout supports the following continuous integration servers:
    * Hudson
    * Jenkins
    * TeamCity (planned)

I'll add any requested CI server that has a RESTful API, and for which I can get
a demo installation to test it.


Installation:
==================

    $ git clone git://github.com/ChristopherMacGown/roundabout.git
    $ cd roundabout
    $ cp roundabout.cfg{-example,}
    $ vi roundabout.cfg # SEE Configuration
    $ sudo python setup.py install


Configuration:
==================
Roundabout's configuration file is a JSON file consisting of the following
sections:

## default
### logfile: string
  The full path to roundabout's logfile.
### lgtm: string
  The default string roundabout will look for from the configured github_core_team
### min_lgtm_count: integer
  A *future* configuration option that will check for a minimum of N lgtms
### use_merge_tag: string
  A *future* configuration option that will use the existence of a tag in addition
  to the minimum lgtms to determine if a pull_request should be processed.

## ci
### class: string
  Lowercase name of the CI server you're using.

  Valid options:

     * hudson
     * jenkins
### username: string
  The username for the CI api.
### password: string
  The password for the CI api.
### job: string
  I'm not certain this will be required in future CI servers, but hudson/jenkins
  calls each project a job. This is the name of that project/job. In the *future*
  should probably change to something more generic.
### base_url: string
  The base URL for the CI instance. For example: http://hudson.atomicpony.com
## git
### squash_merges: boolean
  Whether or not you want roundabout to merge --squash or not. If false, the
  resulting merges will be interleaved. Otherwise will be squashed into a
  single commit.
### base_repo_url: string
  The URL for the git repo. This doesn't need to be a github url, but the
  user roundabout runs as *must* be able to write to this repo. Or things just
  won't work.
### local_repo_path: string
  The full repo to where roundabout will clone the pull request repos.
## github
### username: string
  The github username with write permission to the repository.
### api_token: string
  The github API token for the above user.
### repo: string
  The "account/repository" identifier for the repository. 
  For example: "ChristopherMacGown/roundabout"
### organization: string
  In order to get the list of authorized 'lgtmers', roundabout requires an
  organization with a team created. This is the name of the organization.
  For Example: "atomicpony"
### core_team: string
  The organization team with the list of authorized 'lgtmers'.
  For Example: "atomic pony core"
### req_per_second: integer
  github's API rate limits incoming requests, so there's no point in increasing
  this over 1. If it becomes possible to get a higher throughput on requests
  per second, here's where you'd configure it.
### http_proxy_host: string
  A optional http proxy hostname for github2's proxy support.
### http_proxy_port: integer
  A optional http proxy port for github2's proxy support.
## pylint
  This is an optional configuration option.
### modules: array of strings
  The list of modules you want to run pylint against. Syntax is identical to
  pylint's command line interface.
### current_score: integer
  The current number of pylint violations. This should be set very high for the
  first run if you don't know what the current_score will be on the system
  running roundabout.

  If this value is smaller than the value of max_score, any merge that has a
  higher number of pylint violations than the current_score will fail.
### max_score: integer
  The maximum number of pylint violations you're willing to accept into your
  code base. If this value is larger than the value of current_score, any
  merge that has a higher number of pylint violations than the current_score
  will fail.

Use:
==================

After installing and configuring roundabout can be started, stopped, and run:

    $ roundabout --config_file=path/to/your-config-file start
    $ roundabout --config_file=path/to/your-config-file stop
    $ roundabout --config_file=path/to/your-config-file run


After roundabout is running, it will automatically process any pull_requests on
the configured github repo that are LGTMed by your core team.


Please see the following workflow:

![roundabout workflow](https://github.com/ChristopherMacGown/roundabout/raw/master/roundabout.png)


Required packages:
==================

* GitPython==0.3.1
* github2>=0.2.0
* pylint==0.22.0

If you want to run the unittests:

* coverage
* nose
