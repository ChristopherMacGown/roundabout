import time
import unittest
from roundabout.config import Config, ConfigError
from tests import utils 


class ConfigTestCase(unittest.TestCase):
    _test_bad_config_file = "tests/data/bad.cfg"
    _test_good_config_file = "tests/data/good.cfg"

    def setUp(self):
        self.t = time.time()

    def tearDown(self):
        print "%s: %f" % (self.id(), time.time() - self.t)

    def test_that_underunder_getattr_returns_sanity(self):
        config = Config(config_files=[self._test_good_config_file])
        self.assertEqual(config.__getattr__('nothing_here'), None)
        self.assertEqual(config.__getattr__('test_attribute'), 12345)

    def test_that_parsing_works(self):
        config = Config(config_files=[self._test_good_config_file])
        self.assertTrue(config.test_attribute)
        self.assertFalse(config.test_false_attribute)

    def test_raises_config_error_on_bad_parse(self):
        self.assertRaises(ConfigError, Config, config_files=[None])
        self.assertRaises(ConfigError, Config,
                          config_files=[self._test_bad_config_file])
