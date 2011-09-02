import json
import time
import unittest
from roundabout.config import Config, ConfigError
from tests import utils 


class ConfigTestCase(utils.TestHelper):
    _test_bad_config_file = utils.testdata("bad.cfg")
    _test_good_config_file = utils.testdata("good.cfg")
    _test_horrible_config_file = utils.testdata("horrible.cfg")
    _test_bad_optional_config_file = utils.testdata("bad_optional.cfg")

    def setUp(self):
        self.t = time.time()

    def tearDown(self):
        print "%s: %f" % (self.id(), time.time() - self.t)

    def test_that_config_parsing_and_get_returns_sanity(self):
        config = Config(config_file=self._test_good_config_file)
        self.assertTrue(config["github"])
        self.assertEqual(config["github"]["req_per_second"], 1)
        self.assertEqual(config["github"]["username"], "YOUR GITHUB USERNAME")

    def test_that_update_works(self):
        config = Config(config_file=utils.testdata("good.cfg"))
        self.assertCalled(json.dump, config.update, "pylint","max_score", 10000)

    def test_raises_config_error_on_bad_parse(self):
        self.assertRaises(ConfigError, Config, config_file=None)
        self.assertRaises(ConfigError, Config,
                          config_file=self._test_horrible_config_file)

    def test_raises_config_error_on_improper_configuration(self):
        self.assertRaises(ConfigError, Config, 
                          config_file=self._test_bad_config_file)

    def test_raises_config_error_on_bad_optional_config(self):
        self.assertRaises(ConfigError, Config, 
                          config_file=self._test_bad_optional_config_file)
