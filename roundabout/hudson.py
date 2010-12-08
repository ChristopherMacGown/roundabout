

class Hudson(object):
    @classmethod
    def spawn_job(cls, branch_name):
        # return cls(stuff)
        pass

    @property
    def complete(self):
        """ Get the results from the current job """
        return True

    def __init__(self, stuff):
        pass


    def __nonzero__(self):
        return (self.complete 
                and self.success 
                and self.clean_pylint 
                and self.good_coverage)
