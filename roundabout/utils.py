import json
import os
import optparse
import yaml

from roundabout import log


def optionparser():
    """
    Return an :mod:`optparse` parser for parsing command line options.
    """

    usage_msg = "usage: %prog [options] (start|stop|restart|run|update_config)"



    parser = optparse.OptionParser(usage=usage_msg)
    parser.add_option("--config_file",
                      dest="config_file",
                      help="path to the configuration file")
    return parser


def update_config(config_file):
    """ Update the configuration from yaml to json """

    if not config_file:
        raise RuntimeError("You didn't specify a configuration file")

    try:
        bak_file = config_file + '-bak'
        log.info("moving %s to %s" % (config_file, bak_file))

        os.rename(config_file, bak_file)
        with open(bak_file) as bak:
            log.info("Opening %s" % bak_file)
            with open(config_file, "w") as out:
                log.info("Writing %s" % config_file)
                json.dump(yaml.load(bak), out, indent=4)
    except yaml.YAMLError, e:
        log.info("Couldn't read a yaml file, so nothing needed to be done")
