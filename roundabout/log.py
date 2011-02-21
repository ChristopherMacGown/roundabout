""" Helper methods for logging """

import logging
import logging.handlers
import time


LOGGER = logging.getLogger(name="roundabout")


def init_logger(config, stream=False):
    log_level = logging.DEBUG 

    if stream:
        handler = logging.StreamHandler()
    else:
        log_level = config.default_log_level or log_level
        handler = logging.handlers.RotatingFileHandler(config.default_logfile,
                                                       backupCount=5)

    LOGGER.setLevel(log_level)
    LOGGER.addHandler(handler)


def info(message):
    """ Log the message at info level. """
    LOGGER.info("[%s] %s" % (time.strftime("%d-%m-%Y %H:%M:%S"), message))


def error(message):
    """ Log the message at error level. """
    LOGGER.error("[%s] %s" % (time.strftime("%d-%m-%Y %H:%M:%S"), message))
