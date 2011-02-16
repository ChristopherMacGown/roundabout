#   Copyright 2010 Christopher MacGown
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


DEFAULTS = ("roundabout.cfg",        # Sane Defaults
            "/etc/roundabout.cfg",   # Site level configs
            "~/.roundabout.cfg")     # Are we running as a user?

SECTION_KEY_RE = re.compile("(?P<section>.*?)_(?P<key>.*)")


def _get_key(key):
    """ Return the section and key from a blah_somekey configuration entry """
    match = SECTION_KEY_RE.match(key)
    return match.group('section'), match.group('key')


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

    def __init__(self, config_files=DEFAULTS):
        for config_file in config_files:
            try:
                with open(config_file) as fp:
                    self.__dict__.update(json.load(fp))
            except (TypeError, ValueError, IOError):
                pass

        if not self.__dict__:
            raise ConfigError("Didn't find configuration files, bailing.")

    def __getattr__(self, item):
        try:
            section, key = _get_key(item)
            section_dict = self.__dict__.get(section, {})
            return section_dict.get(key, None)
        except (AttributeError, ValueError):
            return None

    def update(self, key, value):
        """ Update the config and write it to disk """
        # todo(chris): Either generalize this for json/yaml or throw one away.

        section, key = _get_key(key)
        self.__dict__[section][key] = value
        with open('roundabout.cfg', 'w') as fp:
            json.dump(self.__dict__, fp, indent=4)

    def _parse_config_file(self, config_file):
        """
        Parses a configuration file as a dict and populates __dict__ with them.
        """

