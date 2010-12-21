

class Hudson(object):
    @classmethod
    def spawn_job(cls, branch_name):
        return cls()

    @property
    def complete(self):
        """ Get the results from the current job """
        return True

    def __nonzero__(self):
        return False
        # return (self.complete 
        #         and self.success 
        #         and self.clean_pylint 
        #         and self.good_coverage)
