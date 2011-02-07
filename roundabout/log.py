import logging
import logging.handlers
import time
from roundabout.config import Config

CONFIG = Config()
LOGGER = logging.getLogger(name="roundabout")
LOGGER.setLevel(CONFIG.default_log_level or logging.DEBUG)
LOGGER.addHandler(logging.handlers.RotatingFileHandler(CONFIG.default_logfile,
                                                       backupCount=5))

def info(message):
    LOGGER.info("[%s] %s" % (time.strftime("%d-%m-%Y %H:%M:%S"), message))

def error(message):
    LOGGER.error("[%s] %s" % (time.strftime("%d-%m-%Y %H:%M:%S"), message))
