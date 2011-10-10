""" module to run pylint """

import os

PYLINT_CMD = "PYTHONPATH=%s pylint --rcfile=%s -f parseable -r no -dI %s"
PYLINT_FAIL_MSG = "Rejecting due to increased pylint score: %s %s"


class Pylint(object):
    """ wrapper class around pylint """
    def __init__(self, modules, config, path='.'):
        self.modules = modules
        self.config = config
        self.path = path
        self.current_score = 0
        self.previous_score = self.config["pylint"]["current_score"]
        self.max_score = self.config["pylint"]["max_score"]

    def __nonzero__(self):
        return self.__check_pylint()

    def __check_pylint(self):
        """
        Call pylint and return whether or not the current pylint is no
        higher than the previous score or the maximum.
        """

        if 'pylintrc_path' in self.config["pylint"]:
            pylint_path = os.path.join( self.path, self.config["pylint"]["pylintrc_path"] )
        else:
            pylint_path = os.path.join( self.path, 'pylintrc' )

        results = os.popen(PYLINT_CMD % (self.path,
                                         os.path.join(self.path, 'pylintrc'),
                                         str.join(' ', list(self.modules))))
        messages = [message for message in results.read().splitlines()]
        self.config.update('pylint', 'current_score', len(messages))
        self.current_score = self.config["pylint"]["current_score"]

        return self.current_score <= self.previous_score <= self.max_score
