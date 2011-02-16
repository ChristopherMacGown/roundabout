""" Helper methods for logging """

import logging
import logging.handlers
import time
from roundabout.config import Config, ConfigError


try:
    CONFIG = Config()
    LOG_LEVEL = CONFIG.default_log_level
    LOG_HANDLER = logging.handlers.RotatingFileHandler(CONFIG.default_logfile,
                                                       backupCount=5)
except ConfigError:
    LOG_LEVEL = logging.DEBUG
    LOG_HANDLER = logging.StreamHandler()

LOGGER = logging.getLogger(name="roundabout")
LOGGER.setLevel(LOG_LEVEL)
LOGGER.addHandler(LOG_HANDLER)

def info(message):
    """ Log the message at info level. """
    LOGGER.info("[%s] %s" % (time.strftime("%d-%m-%Y %H:%M:%S"), message))

def error(message):
    """ Log the message at error level. """
    LOGGER.error("[%s] %s" % (time.strftime("%d-%m-%Y %H:%M:%S"), message))
