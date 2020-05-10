import unittest
import json
from visiobas.gate_client import VisiobasGateClient
from bacnet.bacnet import ObjectProperty
from test_visiobas import test_config
import config.logging

USING_SERVER = "local"

HOST = test_config.SERVER[USING_SERVER]["host"]
PORT = test_config.SERVER[USING_SERVER]["port"]
USER = test_config.SERVER[USING_SERVER]["user"]
PWD = test_config.SERVER[USING_SERVER]["pwd"]


class TestVisiobasDataCollector(unittest.TestCase):
    def setUp(self):
        config.logging.initialize_logging()
        self.client = VisiobasGateClient(HOST, PORT, verify=False)
        self.client.rq_login(USER, PWD)

    def tearDown(self):
        self.client.rq_logout()

    def test_start_collecting(self):
        devices = self.client.rq_devices()
        for device in devices:
            property_list = json.loads(device[ObjectProperty.PROPERTY_LIST.id()])
            print(property_list)


if __name__ == '__main__':
    unittest.main()
