import os
import unittest
import visiobas.logging
import logging
from bacnet.parser import BACnetParser


class BACnetParserTest(unittest.TestCase):
    def setUp(self):
        visiobas.logging.initialize_logging()
        self.logger = logging.getLogger(__name__)

    def test_bacrpm_parser(self):
        path = "{}/resource/bacrpm.txt".format(os.path.dirname(os.path.abspath(__file__)))
        self.logger.debug("reading test file: {}".format(path))
        with open(path, "r") as file:
            text = file.read()
            self.logger.debug("{} content:\n{}".format(path, text))
            parser = BACnetParser()
            objects = parser.parse_bacrpm(text)
            self.assertTrue(objects is not None)


if __name__ == '__main__':
    unittest.main()
