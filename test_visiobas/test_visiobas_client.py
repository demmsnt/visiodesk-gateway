import unittest
from visiobas.client import VisiobasClient
from visiobas.gate_client import VisiobasGateClient
from bacnet.bacnet import ObjectType
from bacnet.bacnet import ObjectProperty
import config.logging
from random import randrange
from test_visiobas import test_config
from visiobas.object.bacnet_object import BACnetObject, Device
from visiobas import visiodesk

USING_SERVER = "local"

HOST = test_config.SERVER[USING_SERVER]["host"]
PORT = test_config.SERVER[USING_SERVER]["port"]
USER = test_config.SERVER[USING_SERVER]["user"]
PWD = test_config.SERVER[USING_SERVER]["pwd"]


class TestVisiobasClient(unittest.TestCase):
    def setUp(self):
        config.logging.initialize_logging()
        self.client = VisiobasClient(HOST, PORT, verify=False)
        self.client.rq_login(USER, PWD)

    def tearDown(self):
        self.client.rq_logout()

    def test_get_children(self):
        objects = self.client.rq_children()
        self.assertTrue(len(objects) > 0)

        reference = objects[0][ObjectProperty.OBJECT_PROPERTY_REFERENCE.id()]
        objects = self.client.rq_children(reference)
        self.assertTrue(len(objects) >= 0)


class TestVisiobasGateClient(unittest.TestCase):
    def setUp(self):
        config.logging.initialize_logging()
        self.client = VisiobasGateClient(HOST, PORT, verify=False)
        self.client.rq_login(USER, PWD)

    def tearDown(self):
        self.client.rq_logout()

    def test_get_object(self):
        o = self.client.rq_vbas_get_object("Site:Blok_A/Temperature")
        self.assertIsNotNone(o)
        self.assertEqual("Site:Blok_A/Temperature", o[ObjectProperty.OBJECT_PROPERTY_REFERENCE.id()])
        print(o)

    def test_rq_device_list(self):
        devices = self.client.rq_devices()
        self.assertTrue(type(devices) is list)
        self.assertTrue(len(devices) > 0)

    def test_device_configuration_files(self):
        # test device 200 - expected filled configuration files with host: 127.0.0.1 and port 80
        devices = self.client.rq_devices()
        for o in devices:
            if not o[ObjectProperty.OBJECT_IDENTIFIER.id()] == 200:
                continue
            device = Device(o)
            port = device.get_port()
            host = device.get_host()
            self.assertTrue(host == "127.0.0.1")
            self.assertTrue(port == 80)

    def test_rq_device_objects(self):
        objects = self.client.rq_device_invalid_objects(200)
        self.assertTrue(objects is not None)

    def test_rq_binary_input(self):
        objects = self.client.rq_device_object(200, ObjectType.BINARY_INPUT)
        self.assertTrue(type(objects) is list)

    def test_rq_put(self):
        device_id = 200
        objects = self.client.rq_device_object(device_id, ObjectType.ANALOG_INPUT)
        data = []
        for o in objects:
            d = {
                ObjectProperty.OBJECT_IDENTIFIER.id(): o[ObjectProperty.OBJECT_IDENTIFIER.id()],
                ObjectProperty.OBJECT_PROPERTY_REFERENCE.id(): o[ObjectProperty.OBJECT_PROPERTY_REFERENCE.id()],
                ObjectProperty.DEVICE_ID.id(): device_id,
                ObjectProperty.PRESENT_VALUE.id(): randrange(100),
                ObjectProperty.OBJECT_TYPE.id(): o[ObjectProperty.OBJECT_TYPE.id()]
            }
            data.append(d)
        self.client.rq_put(device_id, data)

    def test_rq_notification_class(self):
        # not pass
        object = self.client.rq_get_device_objects(device_id=1,
                                                   object_id=1501,
                                                   object_type=ObjectType.NOTIFICATION_CLASS)
        self.assertTrue(object is not None)

    def test_rq_notification_classes(self):
        objects = self.client.rq_device_object(device_id=1,
                                               object_type=ObjectType.NOTIFICATION_CLASS)
        self.assertTrue(type(objects) is list)

    def test_rq_get_vdesk_status_list(self):
        l = self.client.rq_vdesk_get_status_list()
        self.assertTrue(l is not None)
        self.assertTrue(type(l) is list)
        print(l)

    def test_rq_get_vdesk_priorities(self):
        l = self.client.rq_vdesk_get_priorities()
        self.assertTrue(l is not None)
        self.assertTrue(type(l) is l)
        print(l)

    def test_rq_get_vdesk_support_levels(self):
        l = self.client.rq_vdesk_get_support_levels()
        self.assertTrue(l is not None)
        self.assertTrue(type(l) is list)
        print(l)

    def test_rq_get_vdesk_user_types(self):
        l = self.client.rq_vdesk_get_user_types()
        self.assertTrue(l is not None)
        self.assertTrue(type(l) is list)
        print(l)

    def test_rq_get_vdesk_topic_type_items(self):
        l = self.client.rq_vdesk_get_topic_type_items()
        self.assertTrue(l is not None)
        self.assertTrue(type(l) is list)
        print(l)

    def test_rq_get_vdesk_topic_types(self):
        l = self.client.rq_vdesk_get_topic_types()
        self.assertTrue(l is not None)
        self.assertTrue(type(l) is list)
        print(l)

    def test_rq_get_vdesk_groups(self):
        l = self.client.rq_vdesk_get_groups()
        self.assertTrue(l is not None)
        self.assertTrue(type(l) is list)
        print(l)

    def test_rq_vdesk_get_users_by_group(self):
        l = self.client.rq_vdesk_get_users_by_group()
        self.assertTrue(l is not None)
        self.assertTrue(type(l) is list)
        print(l)

    def test_rq_vdesk_get_users(self):
        l = self.client.rq_vdesk_get_users()
        self.assertTrue(l is not None)
        self.assertTrue(type(l) is list)
        print(l)

    def test_rq_vdesk_get_user_by_id(self):
        l = self.client.rq_vdesk_get_user_by_id(1)
        self.assertTrue(l is not None)
        self.assertTrue(type(l) is list)
        print(l)

    def test_rq_vdesk_add_topic(self):
        some_object = BACnetObject(self.client.rq_device_object(200, ObjectType.ANALOG_INPUT)[0])
        description = some_object.get_description()
        reference = some_object.get_object_reference()
        topic_title = description if description else reference

        groups = self.client.rq_vdesk_get_groups()
        found = next(filter(lambda g: g["name"] == "VisioDESK", groups), None)
        if found is None:
            self.assertTrue(False)
        data = {
            "name": topic_title,
            "topic_type": {
                "id": visiodesk.TopicType.EVENT.id()
            },
            "items": [
                {
                    "type": {
                        "id": visiodesk.ItemType.PRIORITY.id()
                    },
                    "priority": {
                        "id": visiodesk.TopicPriority.HEED.id()
                    },
                    "text": visiodesk.TopicPriority.HEED.name(),
                    "name": "Повышенный",
                    "like": 0
                },
                {
                    "type": {
                        "id": visiodesk.ItemType.STATUS.id()
                    },
                    "status": {
                        "id": visiodesk.TopicStatus.NEW.id()
                    },
                    "text": visiodesk.TopicStatus.NEW.name(),
                    "name": "Новая",
                    "like": 0
                },
                {
                    "type": {
                        "id": visiodesk.ItemType.MESSAGE.id()
                    },
                    "text": reference,
                    "name": "Сообщение",
                    "like": 0
                }
            ],
            "groups": [
                {"id": found["id"]}
            ],
            "description": "[p]{} out of limits[/p]".format(topic_title)
        }
        self.client.rq_vdesk_add_topic(data)

    def test_rq_vdesk_add_topic_item(self):
        groups = self.client.rq_vdesk_get_groups()
        found = next(filter(lambda g: g["name"] == "VisioDESK", groups), None)
        if found is None:
            self.assertTrue(False)
        # unit test not ready
        self.assertTrue(False)
        self.client.rq_vdesk_add_topic_item(None)

    def test_rq_vdesk_get_topic_by_user(self):
        topics = self.client.rq_vdesk_get_topic_by_user()
        self.assertTrue(topics is not None)
        self.assertTrue(type(topics) is list)
        for topic in topics:
            print(topic)

    def test_rq_vdesk_get_topic_by_id(self):
        topic = self.client.rq_vdesk_get_topic_by_id(1)
        self.assertIsNotNone(topic)
        print(topic)


# ERROR 2020-04-19 20:44:09,596 __main__ run      Failed put data: {'79': 'analog-input', '75': 25307.0, '85': '52.13', '846': 200}

if __name__ == '__main__':
    unittest.main()
