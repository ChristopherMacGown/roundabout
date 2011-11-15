import json
import time
from roundabout import config
from roundabout import pylint 
from tests import utils


class PylintTestCase(utils.TestHelper):
    def setUp(self):
        self.t = time.time()

    def tearDown(self):
        print "%s: %f" % (self.id(), time.time() - self.t)

    def test_pylint_runs(self):
        cfg = config.Config(utils.testdata('good.cfg'))
        p = pylint.Pylint(['tests'], config=cfg)
        self.assertTrue(p)
        cfg.update("pylint", "current_score", 1000)
