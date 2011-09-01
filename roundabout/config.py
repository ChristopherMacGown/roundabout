#   Copyright 2010 Christopher MacGown
#   Modifications Copyright 2011 Piston Cloud Computing, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
# -*- coding: utf-8 -*-


""" roundabout config singleton """
import re
import json


BAD_MANDATORY_MSG = "Bad mandatory configuration, expected '%s' %s." 
BAD_OPT_MSG = "Bad optional config, expected %s for %s."
DEFAULT = "roundabout.cfg"
MANDATORY_KEYS = {
    "default": ["logfile", "lgtm"],
    "git": ["base_repo_url", "local_repo_path", "squash_merges"],
    "ci": ["class", "username", "password", "job", "base_url"],
    "github": ["username", "core_team", "repo",
               "api_token", "organization", "req_per_second",],
    }
OPTIONAL_KEYS = {
    "pylint": ["modules", "max_score", "current_score"],
    }
SECTION_KEY_RE = re.compile("(?P<section>.*?)_(?P<key>.*)")


class ConfigError(Exception):
    """ A config error """
    pass


class Config(object):
    """
    All configuration options are set as properties on this object with in
    the format of sectionname_key.

    For example:
       {"server": {"hostname": "somehost"}} -> Config().server_hostname
    """

    def __init__(self, config_file):
        try:
            with open(config_file) as fp:
                self.__dict__.update(json.load(fp))
        except (TypeError, ValueError, IOError):
            pass
    
        self.validate()
        self.config_file = config_file

    def __getitem__(self, key):
        return self.__dict__[key]

    def update(self, section, key, value):
        """ Update the config and write it to disk """

        self.__dict__[section][key] = value

        updated_dict = self.__dict__.copy()
        updated_dict.pop('config_file')

        with open(self.config_file, 'w') as fp:
            json.dump(updated_dict, fp, indent=4)

    def validate(self):
        """Walk the configuration and make sure that it has all the expected
        mandatory keys, and for any optional config that it has all the expected
        keys for that.
        """

        if not self.__dict__:
            raise ConfigError("Didn't find configuration files, bailing.")
        
        for key in MANDATORY_KEYS.keys():
            if not key in self.__dict__.keys():
                raise ConfigError(BAD_MANDATORY_MSG % (key, ""))

            for sub_key in MANDATORY_KEYS[key]:
                if not sub_key in self.__dict__[key]:
                    raise ConfigError(BAD_MANDATORY_MSG % (key, sub_key))

        for key in OPTIONAL_KEYS.keys():
            if not key in self.__dict__.keys():
                self.__dict__[key] = None
                continue
            
            for sub_key in OPTIONAL_KEYS[key]:
                if not sub_key in self.__dict__[key]:
                    # NOTE(chris): Should this delete the optional config?
                    raise ConfigError(BAD_OPT_MSG % (key, sub_key))
