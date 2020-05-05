import os
import unittest
import visiobas.visiobas_logging
import logging
from bacnet.parser import BACnetParser
from bacnet.writer import BACnetWriter
from bacnet.bacnet import bacnet_name_map
from bacnet.bacnet import ObjectProperty


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
            self.assertTrue(object[ObjectProperty.OBJECT_IDENTIFIER.id()], 3000022)
            self.assertTrue(object[ObjectProperty.OBJECT_TYPE.id()], "analog-input")

    def test_bacwi_parser(self):
        path = "{}/resource/address_cache".format(os.path.dirname(os.path.abspath(__file__)))
        self.logger.debug("reading test file: {}".format(path))
        with open(path, "r") as file:
            text = file.read()
            self.logger.debug("{} content:\n{}".format(path, text))
            devices = BACnetParser.parse_bacwi(text)
            self.assertTrue(len(devices) == 5)
            self.assertTrue(devices[0]["id"] == 200)
            # 0A:15:50:0C:BA:C0
            self.assertTrue(devices[0]["host"] == "10.21.80.12")
            self.assertTrue(devices[0]["port"] == 47808)

    def test_bacwi_writer(self):
        devices = [{
            "id": 200,
            "host": "10.21.80.12",
            "port": 47808,
            "apdu": 480}]
        text = BACnetWriter.create_bacwi(devices)
        self.assertTrue(text is not None)
        self.assertTrue(len(text) > 0)
        print(text)

    def test_bacwi_writer_reader(self):
        devices = [{
            "id": 200,
            "host": "10.21.80.12",
            "port": 47808,
            "apdu": 480}]
        text = BACnetWriter.create_bacwi(devices)
        devices = BACnetParser.parse_bacwi(text)
        self.assertTrue(len(devices) == 1)
        self.assertTrue(devices[0]["id"] == 200)
        self.assertTrue(devices[0]["host"] == "10.21.80.12")
        self.assertTrue(devices[0]["port"] == 47808)

if __name__ == '__main__':
    unittest.main()
