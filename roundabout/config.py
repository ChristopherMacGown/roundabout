"""
   Copyright 2010 Christopher MacGown

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
# -*- coding: utf-8 -*-

""" roundabout config singleton """

def parse_config_yaml(cfg):
    """ Lazy load yaml and try to load a configuration """

    try:
        import yaml
        return yaml.load(cfg)  # Returns None which sucks.
    except yaml.parser.ParserError as e:
        raise ValueError(e.args)


def parse_config_json(cfg):
    """ Lazy load json and try to decode the configuration """

    import json
    return json.JSONDecoder().decode(cfg)


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

    def __new__(cls, *args, **kwargs):
        self = object.__new__(cls)
        self.__dict__ = cls.__shared_state__
        return self

    def __init__(self, config_files=__default_configs):
        if not self.__dict__:
            print "Assimilating your biological distinctiveness"
            for config_file in config_files:
                self._parse_config_file(config_file)

            if not self.__dict__:
                raise ConfigError("Didn't find configuration files, bailing.")

    def __getattr__(self, item):
        return self.__dict__.get(item, None)

    def _parse_config_file(self, config_file):
        """ Parses a configuration file as a dict and populates __dict__
        with them. __dict__ is Config.__shared_state
        """

        parsers = (parse_config_json, parse_config_yaml)

        try:
            with open(config_file) as fp:
                cfg = fp.read()

                config = None
                for parser in parsers:
                    try:
                        config = parser(cfg)
                        if config:
                            break
                    except (ValueError, ImportError):
                        pass

                for (section_name, section) in config.items():
                    for (item, value) in section.items():
                        config_attr = "%s_%s" % (section_name, item)
                        self.__setattr__(config_attr, value)
        except (AttributeError, TypeError, IOError):
            pass
