""" module to run pylint """

import os

from roundabout import config

PYLINT_CMD = "PYTHONPATH=%s pylint --rcfile=%s -f parseable -r no -dI %s"
PYLINT_FAIL_MSG = "Rejecting due to increased pylint score: %s %s"


class Pylint(object):
    """ wrapper class around pylint """
    def __init__(self, modules, cfg=config.Config(), path='.'):
        self.modules = modules
        self.cfg = cfg
        self.path = path
        self.current_score = 0
        self.previous_score = self.cfg.pylint_current_score
        self.max_score = self.cfg.pylint_max_score

    def __nonzero__(self):
        return self.__check_pylint()

    def __check_pylint(self):
        """
        Call pylint and return whether or not the current pylint is no 
        higher than the previous score or the maximum.
        """

        results = os.popen(PYLINT_CMD % (self.path, self.path,
                                         str.join(' ', list(self.modules))))
        messages = [message for message in results.read().splitlines()]
        self.cfg.update('pylint_current_score', len(messages))
        self.current_score = self.cfg.pylint_current_score

        return self.current_score <= self.previous_score <= self.max_score
