from utilities.config import ConfigFileReader
import yaml
from pyfakefs.fake_filesystem_unittest import TestCase


class TestConfigFileReader(TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_read_config(self):
        # create a fake config file for testing
        test_config = {"key1": "value1", "key2": 2}
        self.fs.create_dir("game_manager/config")
        with open("game_manager/config/test_config.yml", "w") as f:
            yaml.dump(test_config, f)

        # test the ConfigFileReader class
        reader = ConfigFileReader("test_config.yml")
        config = reader.get_config()
        self.assertEqual(config, test_config)

    def tearDown(self):
        self.tearDownPyfakefs()
