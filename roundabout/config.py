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
import yaml

SECTION_KEY_RE = re.compile("(?P<section>.*?)_(?P<key>.*)")

def parse_config_yaml(cfg):
    """ Lazy load yaml and try to load a configuration """

    try:
        return yaml.load(cfg)  # Returns None which sucks.
    except yaml.parser.ParserError as e:
        raise ValueError(e.args)


def parse_config_json(cfg):
    """ Lazy load json and try to decode the configuration """

    import json
    return json.JSONDecoder().decode(cfg)

def _get_key(key):
    """ Return the section and key from a blah_somekey configuration entry """
    match = SECTION_KEY_RE.match(key)
    return match.group('section'), match.group('key')

class ConfigError(Exception):
    """ A config error """
    pass


class Config(object):
    """ Borg style Config object, the shared state is only initialized once.
    All configuration options are set as properties on this object with in
    the format of sectionname_key.

    For example:
       {"server": {"hostname": "somehost"}} -> Config().server_hostname
    """

    __default_configs = ("roundabout.cfg",        # Sane Defaults
                         "/etc/roundabout.cfg",   # Site level configs
                         "~/.roundabout.cfg")     # Are we running as a user?
    __shared_state__ = {}

    def __new__(cls, config_files=__default_configs): #pylint: disable=W0613
        self = object.__new__(cls)
        self.__dict__ = cls.__shared_state__
        return self

    def __init__(self, config_files=__default_configs):
        if not self.__dict__:
            for config_file in config_files:
                self._parse_config_file(config_file)

            if not self.__dict__:
                raise ConfigError("Didn't find configuration files, bailing.")

    def __getattr__(self, item):
        section, key = _get_key(item)
        section_dict = self.__dict__.get(section, {})
        return section_dict.get(key, None)

    def update(self, key, value):
        """ Update the config and write it to disk """
        # todo(chris): Either generalize this for json/yaml or throw one away.

        section, key = _get_key(key)
        self.__dict__[section][key] = value
        with open('roundabout.cfg', 'w') as fp:
            yaml.dump(self.__dict__, fp, default_flow_style=False)

    def _parse_config_file(self, config_file):
        """ Parses a configuration file as a dict and populates __dict__
        with them. __dict__ is Config.__shared_state
        """

        parsers = (parse_config_json, parse_config_yaml)

        try:
            with open(config_file) as fp:
                cfg = fp.read()
                for parser in parsers:
                    try:
                        self.__dict__.update(parser(cfg))
                        if self.__dict__:
                            break
                    except (ValueError, ImportError):
                        pass
        except (AttributeError, TypeError, IOError):
            pass
