from roundabout import config
from roundabout import pylint 
from tests import utils


class PylintTestCase(utils.TestHelper):
    def test_pylint_runs(self):
        cfg = config.Config(config_files=[utils.testdata('pylint.cfg')])
        p = pylint.Pylint(['tests'], config=cfg)
        self.assertTrue(p)
