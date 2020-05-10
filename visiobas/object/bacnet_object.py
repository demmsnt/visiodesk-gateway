import enum
import json
from bacnet.bacnet import ObjectProperty, ObjectType
from visiobas.visiodesk import TopicPriority


class Transition(enum.Enum):
    TO_OFFNORMAL = 0
    TO_FAULT = 1
    TO_NORMAL = 2

    def id(self):
        return self.value


class BACnetObject:
    def __init__(self, data):
        self._data = data
        self.configuration_files = None
        self._default_update_interval = 3600
        self.property_list = None
        self.notification_object = None

    def __str__(self) -> str:
        return "({}, {}) {}".format(self.get_object_type_name(), self.get_id(), self.get_object_reference())

    def get(self, object_property, default=None):
        property_code = object_property.id() if type(object_property) == ObjectProperty else object_property
        try:
            return self._data[property_code]
        except:
            return default

    def set(self, object_property, value):
        property_code = object_property.id() if type(object_property) == ObjectProperty else object_property
        self._data[property_code] = value

    def get_property_list(self):
        if self.property_list is not None:
            return self.property_list
        else:
            try:
                self.property_list = json.loads(self.get(ObjectProperty.PROPERTY_LIST))
                return self.property_list
            except:
                return None

    def get_id(self):
        return self.get(ObjectProperty.OBJECT_IDENTIFIER)

    def get_configuration_files(self):
        if self.configuration_files is not None:
            return self.configuration_files
        else:
            try:
                self.configuration_files = json.loads(self.get(ObjectProperty.CONFIGURATION_FILES))
                return self.configuration_files
            except:
                return None

    def get_update_interval(self):
        property_list = self.get_property_list()
        if property_list is None:
            return self._default_update_interval
        if 'update_interval' not in property_list:
            return self._default_update_interval
        try:
            return int(property_list['update_interval'])
        except:
            return self._default_update_interval

    def get_device_id(self):
        return self.get(ObjectProperty.DEVICE_ID)

    def get_object_type_code(self):
        return ObjectType.name_to_code(self.get(ObjectProperty.OBJECT_TYPE))

    def get_object_type_name(self):
        return self.get(ObjectProperty.OBJECT_TYPE)

    def get_object_type(self):
        return self.get(ObjectProperty.OBJECT_TYPE)

    def get_object_reference(self):
        return self.get(ObjectProperty.OBJECT_PROPERTY_REFERENCE)

    def get_low_limit(self):
        return self.get(ObjectProperty.LOW_LIMIT)

    def get_high_limit(self):
        return self.get(ObjectProperty.HIGH_LIMIT)

    def get_event_detection_enable(self):
        return self.get(ObjectProperty.EVENT_DETECTION_ENABLE) == 1

    def get_alarm_value(self):
        return self.get(ObjectProperty.ALARM_VALUE)

    def get_alarm_values(self):
        alarm_values = self.get(ObjectProperty.ALARM_VALUES)
        if alarm_values is None:
            return []
        if type(alarm_values) is list:
            return alarm_values
        return []

    def get_notification_class(self):
        try:
            return int(self.get(ObjectProperty.NOTIFICATION_CLASS))
        except:
            return 0

    def set_notification_object(self, notification_object):
        """
        :type notification_object: BACnetObject
        :return:
        """
        self.notification_object = notification_object

    def get_notification_object(self):
        return self.notification_object

    def get_description(self):
        return self.get(ObjectProperty.DESCRIPTION, "")

    def get_data(self):
        return self._data

    def get_status_flags(self):
        return self.get(ObjectProperty.STATUS_FLAGS, [False, False, False, False])

    def set_status_flags(self, flags: list):
        self.set(ObjectProperty.STATUS_FLAGS, flags)

    def get_reliability(self):
        return self.get(ObjectProperty.RELIABILITY, "no-fault-detected")

    def set_reliability(self, reliability):
        self.set(ObjectProperty.RELIABILITY, reliability)

    def get_event_message_texts(self):
        return self.get(ObjectProperty.EVENT_MESSAGE_TEXTS, ["", "", ""])

    def get_event_message_text(self, transition: Transition):
        try:
            return self.get_event_message_texts()[transition.id()]
        except:
            return ""

    def is_notification_allowed(self, transition: Transition):
        try:
            return self.get(ObjectProperty.EVENT_ENABLE, [False, False, False])[transition.id()]
        except:
            return False

    def get_present_value(self):
        return self.get(ObjectProperty.PRESENT_VALUE.id())

    def set_present_value(self, value):
        self.set(ObjectProperty.PRESENT_VALUE.id(), value)


class Device(BACnetObject):
    def __init__(self, data):
        super().__init__(data)

    def get_port(self):
        configuration_files = self.get_configuration_files()
        if configuration_files is None:
            return None
        if "port" not in configuration_files:
            return None
        return configuration_files["port"]

    def get_host(self):
        configuration_files = self.get_configuration_files()
        if configuration_files is None:
            return None
        if "host" not in configuration_files:
            return None
        return configuration_files["host"]

    @staticmethod
    def fromJson(s):
        """
        :param s: json string
        :type s: string
        :return: device object
        """
        return Device(json.loads(s))

    def get_apdu(self):
        default_apdu = 640
        apdu = self.get(ObjectProperty.APDU_TIMEOUT)
        return apdu if apdu is not None else default_apdu

    def set_host(self, host):
        if self.configuration_files is None:
            self.configuration_files = {}
        self.configuration_files['host'] = host

    def set_port(self, port):
        if self.configuration_files is None:
            self.configuration_files = {}
        self.configuration_files['port'] = port

    def set_read_app(self, read_app):
        if self.configuration_files is None:
            self.configuration_files = {}
        self.configuration_files["read"] = read_app

    def get_read_app(self):
        configuration_files = self.get_configuration_files()
        if configuration_files is None:
            return None
        if "read" not in configuration_files:
            return None
        return configuration_files["read"]

    def get_write_app(self):
        configuration_files = self.get_configuration_files()
        if configuration_files is None:
            return None
        if "write" not in configuration_files:
            return None
        return configuration_files["write"]


class NotificationClass(BACnetObject):
    def __init__(self, data):
        super().__init__(data)

    def get_recipient_list(self):
        recipient_list = self.get(ObjectProperty.RECIPIENT_LIST)
        return recipient_list if type(recipient_list) is list else []

    def get_priority(self, transition):
        default = [TopicPriority.TOP, TopicPriority.NORM, TopicPriority.NORM]
        try:
            # TODO make priority enum
            return self.get(ObjectProperty.PRIORITY, default)[transition.id()]
        except:
            return default[transition.id()]
