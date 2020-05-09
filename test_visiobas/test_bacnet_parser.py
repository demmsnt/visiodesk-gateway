import os
import unittest
import visiobas.visiobas_logging
import logging
from bacnet.parser import BACnetParser
from bacnet.writer import BACnetWriter
from bacnet.bacnet import bacnet_name_map
from bacnet.bacnet import ObjectProperty
from bacnet.bacnet import ObjectType
from bacnet.slicer import BACnetSlicer
import bacnet.config


class BACnetParserTest(unittest.TestCase):
    def setUp(self):
        visiobas.visiobas_logging.initialize_logging()
        self.logger = logging.getLogger(__name__)

    def test_bacrp_slicer(self):
        slicer = BACnetSlicer(bacnet.config.visiobas_slicer)
        data = slicer.execute_barp(200, ObjectType.ANALOG_INPUT.id(), 23003, [
            ObjectProperty.PRESENT_VALUE.id(),
            ObjectProperty.STATUS_FLAGS.id()
        ])
        self.assertIn(ObjectProperty.PRESENT_VALUE.id(), data)
        self.assertIn(ObjectProperty.STATUS_FLAGS.id(), data)

    def test_bacrp_parser(self):
        parser = BACnetParser()
        object = {}
        path = "{}/resource/bacrp_reliability.txt".format(os.path.dirname(os.path.abspath(__file__)))
        with open(path, "r") as file:
            parser.parse_bacrp(file.read(), ObjectProperty.RELIABILITY, object)

        path = "{}/resource/bacrp_analog_value_present_value.txt".format(os.path.dirname(os.path.abspath(__file__)))
        with open(path, "r") as file:
            parser.parse_bacrp(file.read(), ObjectProperty.PRESENT_VALUE, object)

        path = "{}/resource/bacrp_description.txt".format(os.path.dirname(os.path.abspath(__file__)))
        with open(path, "r") as file:
            parser.parse_bacrp(file.read(), ObjectProperty.DESCRIPTION, object)

        path = "{}/resource/bacrp_object_identifier.txt".format(os.path.dirname(os.path.abspath(__file__)))
        with open(path, "r") as file:
            parser.parse_bacrp(file.read(), ObjectProperty.OBJECT_IDENTIFIER, object)

        path = "{}/resource/bacrp_out_of_service.txt".format(os.path.dirname(os.path.abspath(__file__)))
        with open(path, "r") as file:
            parser.parse_bacrp(file.read(), ObjectProperty.OUT_OF_SERVICE, object)

        path = "{}/resource/bacrp_status_flags.txt".format(os.path.dirname(os.path.abspath(__file__)))
        with open(path, "r") as file:
            parser.parse_bacrp(file.read(), ObjectProperty.STATUS_FLAGS, object)

        self.assertNotIn(ObjectProperty.RELIABILITY.id(), object)
        self.assertIn(ObjectProperty.PRESENT_VALUE.id(), object)
        self.assertIn(ObjectProperty.DESCRIPTION.id(), object)
        self.assertIn(ObjectProperty.OBJECT_IDENTIFIER.id(), object)
        self.assertIn(ObjectProperty.OBJECT_TYPE.id(), object)
        self.assertIn(ObjectProperty.OUT_OF_SERVICE.id(), object)
        self.assertIn(ObjectProperty.STATUS_FLAGS.id(), object)

        self.assertEqual(object[ObjectProperty.PRESENT_VALUE.id()], 1)
        self.assertEqual(object[ObjectProperty.DESCRIPTION.id()], '""')
        self.assertEqual(object[ObjectProperty.OBJECT_IDENTIFIER.id()], 3000022)
        self.assertEqual(object[ObjectProperty.OBJECT_TYPE.id()], "analog-input")
        self.assertEqual(object[ObjectProperty.OUT_OF_SERVICE.id()], False)
        self.assertEqual(object[ObjectProperty.STATUS_FLAGS.id()], [False, False, False, False])

    def test_apdu_timeout(self):
        path = "{}/resource/bacrpm-emulation-apdu-timeout.txt".format(os.path.dirname(os.path.abspath(__file__)))
        self.logger.debug("reading test_visiobas file: {}".format(path))
        with open(path, "r") as file:
            text = file.read()
            self.logger.debug("{} content:\n{}".format(path, text))
            parser = BACnetParser()
            object = parser.parse_bacrpm(text)
            self.assertTrue(object is not None)
            self.assertTrue(len(object) == 0)

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
            self.assertTrue(object[ObjectProperty.RELIABILITY.id()], "no-fault-detected")

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
