import logging

class LoggingException(BaseException):
    def __init__(self, *args, **kwargs):
        super(LoggingException, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
        if kwargs.get('log'):
            self.logger.error(*args)


class UnknownApproverType(LoggingException):
    pass


class DatabaseError(LoggingException):
    pass
