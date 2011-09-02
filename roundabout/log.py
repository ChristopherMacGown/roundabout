""" Helper methods for logging """

import logging
import logging.handlers
import time


LOGGER = logging.getLogger(name="roundabout")


def init_logger(config, stream=False):
    """Initialize the logger."""

    log_file = config["default"]["logfile"]
    log_level = config["default"].get("log_level", logging.DEBUG)

    if stream:
        handler = logging.StreamHandler()
    else:
        handler = logging.handlers.RotatingFileHandler(log_file, backupCount=5)

    LOGGER.setLevel(log_level)
    LOGGER.addHandler(handler)


def write(message, level):
    """Write a message to the log at the specified level"""
    level("[%s] %s: %s" % (time.strftime("%d-%m-%Y %H:%M:%S"),
                           level.__name__.upper(), message))


def info(message):
    """ Log the message at info level. """
    write(message, LOGGER.info)


def error(message):
    """ Log the message at error level. """
    write(message, LOGGER.error)
