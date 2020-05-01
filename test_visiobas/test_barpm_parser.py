import os
import unittest
import visiobas.visiobas_logging
import logging
from bacnet.parser import BACnetParser
from bacnet.bacnet import bacnet_name_map


class BACnetParserTest(unittest.TestCase):
    def setUp(self):
        visiobas.visiobas_logging.initialize_logging()
        self.logger = logging.getLogger(__name__)

    def test_bacrpm_parser(self):
        path = "{}/resource/bacrpm.txt".format(os.path.dirname(os.path.abspath(__file__)))
        self.logger.debug("reading test_visiobas file: {}".format(path))
        with open(path, "r") as file:
            text = file.read()
            self.logger.debug("{} content:\n{}".format(path, text))
            parser = BACnetParser()
            object = parser.parse_bacrpm(text)
            self.assertTrue(object is not None)
            self.assertTrue(object[bacnet_name_map["object-identifier"]], 3000022)
            self.assertTrue(object[bacnet_name_map["object-type"]], "analog-input")


if __name__ == '__main__':
    unittest.main()
