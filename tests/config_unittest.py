import unittest
from roundabout.config import Config, ConfigError, parse_config_yaml, parse_config_json
from tests import utils 


class ConfigTestCase(unittest.TestCase):
    _test_bad_config_file = "tests/data/bad.cfg"
    _test_good_config_file = "tests/data/good.cfg"

    def setUp(self):
        utils.reset_config()

    def teardown(self):
        utils.reset_config()

    def test_yaml_config(self):
        cfg = parse_config_yaml("---\nfoo: 'bar'")
        self.assertEqual(cfg, {'foo':'bar'})
        self.assertRaises(ValueError, parse_config_yaml, "{{}")

    def test_json_config(self):
        self.assertTrue(parse_config_json('{"foo": "bar"}'))
        cfg = parse_config_json('{"foo": "bar"}')
        self.assertEqual(cfg, {'foo':'bar'})
        self.assertRaises(ValueError, parse_config_json, "{{}")

    def test_that_underunder_getattr_returns_sanity(self):
        config = Config(config_files=[self._test_good_config_file])
        self.assertEqual(config.__getattr__('nothing_here'), None)
        self.assertEqual(config.__getattr__('test_attribute'), 12345)

    def test_that_json_parsing_works(self):
        config = Config(config_files=[self._test_good_config_file])
        self.assertTrue(config.test_attribute)
        self.assertFalse(config.test_false_attribute)

    def test_raises_config_error_on_bad_parse(self):
        self.assertRaises(ConfigError, Config, config_files=[None])
        self.assertRaises(ConfigError, Config,
                          config_files=[self._test_bad_config_file])
