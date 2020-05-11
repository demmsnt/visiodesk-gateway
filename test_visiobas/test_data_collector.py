import unittest
import json
from visiobas.gate_client import VisiobasGateClient
from bacnet.bacnet import ObjectProperty, StatusFlag, StatusFlags, ObjectType
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

    def test_in_alarm_transition(self):
        # initial state
        status_flags = StatusFlags()
        bacnet_object = BACnetObject({
            ObjectProperty.OBJECT_TYPE.id(): ObjectType.ANALOG_INPUT.name(),
            ObjectProperty.HIGH_LIMIT.id(): 50,
            ObjectProperty.LOW_LIMIT.id(): 30,
            ObjectProperty.EVENT_DETECTION_ENABLE.id(): True,
            ObjectProperty.STATUS_FLAGS.id(): status_flags.as_list()
        })
        bacnet_object.set_status_flags(status_flags)
        verifier = VisiobasDataVerifier(None, None, None, None)

        # Transition TO_OFFNORMAL
        # collected data out of range
        data = {ObjectProperty.PRESENT_VALUE.id(): 0}
        status_flags = StatusFlags()
        status_flags.set_in_alarm(False)
        bacnet_object.set_status_flags(status_flags)
        in_alarm, transition = verifier.verify_to_offnormal_transition(bacnet_object, data)
        self.assertEqual(in_alarm, True)
        self.assertEqual(transition, Transition.TO_OFFNORMAL)

        # No Transition but output flag IN_ALARM is False because of in limit range
        # initial BACnetObject state is IN_ALARM
        # collected data in range
        data = {ObjectProperty.PRESENT_VALUE.id(): 40}
        status_flags = StatusFlags()
        status_flags.set_in_alarm(True)
        bacnet_object.set_status_flags(status_flags)
        in_alarm, transition = verifier.verify_to_offnormal_transition(bacnet_object, data)
        self.assertEqual(in_alarm, False)
        self.assertEqual(transition, None)

        # Not Transition, because of collected data is FAULT
        # StatusFlat.IN_ALARM stay unchanged
        data = {"fault": True}
        status_flags = StatusFlags()
        status_flags.set_in_alarm(False)
        bacnet_object.set_status_flags(status_flags)
        in_alarm, transition = verifier.verify_to_offnormal_transition(bacnet_object, data)
        self.assertEqual(in_alarm, bacnet_object.get_status_flag(StatusFlag.IN_ALARM))
        self.assertEqual(transition, None)

        # Not Transition, because of collected data is FAULT
        # StatusFlat.IN_ALARM stay unchanged
        data = {"fault": True}
        status_flags = StatusFlags()
        status_flags.set_in_alarm(True)
        bacnet_object.set_status_flags(status_flags)
        in_alarm, transition = verifier.verify_to_offnormal_transition(bacnet_object, data)
        self.assertEqual(in_alarm, bacnet_object.get_status_flag(StatusFlag.IN_ALARM))
        self.assertEqual(transition, None)

        # Not Transition, because of collected data is FAULT
        # StatusFlat.IN_ALARM stay unchanged
        flags = StatusFlags()
        flags.set_fault(True)
        data = {ObjectProperty.STATUS_FLAGS.id(): flags.as_list()}
        in_alarm, transition = verifier.verify_to_offnormal_transition(bacnet_object, data)
        self.assertEqual(in_alarm, bacnet_object.get_status_flag(StatusFlag.IN_ALARM))
        self.assertEqual(transition, None)

    def test_fault_transition(self):
        # initial state
        status_flags = StatusFlags()
        bacnet_object = BACnetObject({})
        bacnet_object.set_status_flags(status_flags)
        verifier = VisiobasDataVerifier(None, None, None, None)

        # Transition TO_FAULT
        # collected data (sensor offline)
        data = {"fault": True}
        fault, transition = verifier.verify_to_fault_transition(bacnet_object, data)
        self.assertEqual(transition, Transition.TO_FAULT)
        self.assertEqual(fault, True)

        # Transition TO_FAULT
        # collected data RELIABILITY not equal "no-fault-detected"
        data = {ObjectProperty.RELIABILITY.id(): "FAULT DETECTED"}
        fault, transition = verifier.verify_to_fault_transition(bacnet_object, data)
        self.assertEqual(transition, Transition.TO_FAULT)
        self.assertEqual(fault, True)

        # Transition TO_FAULT
        # collected data (sensor online)
        status_flags = StatusFlags()
        status_flags.set_fault(True)
        data = {ObjectProperty.STATUS_FLAGS.id(): status_flags.as_list()}
        fault, transition = verifier.verify_to_fault_transition(bacnet_object, data)
        self.assertEqual(transition, Transition.TO_FAULT)
        self.assertEqual(fault, True)

        # No FAULT transition, initial BACnetObject status flag in FAULT
        bacnet_object.set_status_flag(StatusFlag.FAULT, True)
        data = {"fault": True}
        fault, transition = verifier.verify_to_fault_transition(bacnet_object, data)
        self.assertEqual(transition, None)
        self.assertEqual(fault, True)

        # No FAULT transition, initial BACnetObject status flag in FAULT
        bacnet_object.set_status_flag(StatusFlag.FAULT, True)
        status_flags = StatusFlags()
        status_flags.set_fault(True)
        data = {ObjectProperty.STATUS_FLAGS.id(): status_flags.as_list()}
        fault, transition = verifier.verify_to_fault_transition(bacnet_object, data)
        self.assertEqual(transition, None)
        self.assertEqual(fault, True)

        # No FAULT transition but return FAULT flag should be FALSE because of new data
        bacnet_object.set_status_flag(StatusFlag.FAULT, True)
        data = {
            ObjectProperty.STATUS_FLAGS.id(): [False, False, False, False],
            ObjectProperty.RELIABILITY.id(): "no-fault-detected"
        }
        fault, transition = verifier.verify_to_fault_transition(bacnet_object, data)
        self.assertEqual(transition, None)
        self.assertEqual(fault, False)


if __name__ == '__main__':
    unittest.main()
