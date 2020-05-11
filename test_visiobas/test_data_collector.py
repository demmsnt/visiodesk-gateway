import unittest
import json
from visiobas.gate_client import VisiobasGateClient
from bacnet.bacnet import ObjectProperty, StatusFlag, StatusFlags
from test_visiobas import test_config
import config.logging
from visiobas.object.bacnet_object import BACnetObject, Transition
from data_collector import VisiobasDataVerifier

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

    def test_fault_transition(self):
        # initial state
        status_flags = StatusFlags()
        bacnet_object = BACnetObject({})
        bacnet_object.set_status_flags(status_flags)
        verifier = VisiobasDataVerifier(None, None, None, None)

        # Transition TO_FAULT
        # collected data (sensor offline)
        data = {"fault": True}
        flag, transition = verifier.verify_to_fault_transition(bacnet_object, data)
        self.assertEqual(transition, Transition.TO_FAULT)
        self.assertEqual(flag[0], StatusFlag.FAULT)
        self.assertEqual(flag[1], True)

        # Transition TO_FAULT
        # collected data RELIABILITY not equal "no-fault-detected"
        data = {ObjectProperty.RELIABILITY.id(): "FAULT DETECTED"}
        flag, transition = verifier.verify_to_fault_transition(bacnet_object, data)
        self.assertEqual(transition, Transition.TO_FAULT)
        self.assertEqual(flag[0], StatusFlag.FAULT)
        self.assertEqual(flag[1], True)

        # Transition TO_FAULT
        # collected data (sensor online)
        status_flags = StatusFlags()
        status_flags.set_fault(True)
        data = {ObjectProperty.STATUS_FLAGS.id(): status_flags.as_list()}
        flag, transition = verifier.verify_to_fault_transition(bacnet_object, data)
        self.assertEqual(transition, Transition.TO_FAULT)
        self.assertEqual(flag[0], StatusFlag.FAULT)
        self.assertEqual(flag[1], True)

        # No FAULT transition, initial BACnetObject status flag in FAULT
        bacnet_object.set_status_flag(StatusFlag.FAULT, True)
        data = {"fault": True}
        flag, transition = verifier.verify_to_fault_transition(bacnet_object, data)
        self.assertEqual(transition, None)
        self.assertEqual(flag[0], StatusFlag.FAULT)
        self.assertEqual(flag[1], True)

        # No FAULT transition, initial BACnetObject status flag in FAULT
        bacnet_object.set_status_flag(StatusFlag.FAULT, True)
        status_flags = StatusFlags()
        status_flags.set_fault(True)
        data = {ObjectProperty.STATUS_FLAGS.id(): status_flags.as_list()}
        flag, transition = verifier.verify_to_fault_transition(bacnet_object, data)
        self.assertEqual(transition, None)
        self.assertEqual(flag[0], StatusFlag.FAULT)
        self.assertEqual(flag[1], True)

        # No FAULT transition but return FAULT flag should be FALSE because of new data
        bacnet_object.set_status_flag(StatusFlag.FAULT, True)
        data = {
            ObjectProperty.STATUS_FLAGS.id(): [False, False, False, False],
            ObjectProperty.RELIABILITY.id(): "no-fault-detected"
        }
        flag, transition = verifier.verify_to_fault_transition(bacnet_object, data)
        self.assertEqual(transition, None)
        self.assertEqual(flag[0], StatusFlag.FAULT)
        self.assertEqual(flag[1], False)


if __name__ == '__main__':
    unittest.main()
