""" A single build for a Hudson/Jenkins Job """


class Build(object):
    """ A single build for a Hudson/Jenkins Job """
    # pylint: disable=E1101

    def __init__(self, job, _dict):
        self.__dict__ = _dict
        self.job = job

    def __nonzero__(self):
        return self.complete and self.success

    @property
    def complete(self):
        """ Return whether or not the build is complete. """
        return not self.building

    @property
    def success(self):
        """ Return true if self.result is 'SUCCESS' """
        return self.result == 'SUCCESS'

    def reload(self):
        """ Reload the build. """
        self.__dict__ = [b.__dict__ for b in self.job.builds
                                          if b.number == self.number][0]
        return self
