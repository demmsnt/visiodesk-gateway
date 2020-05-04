import json
from bacnet.bacnet import ObjectProperty, ObjectType


class BACnetObject:
    def __init__(self, data):
        self._data = data
        self.configuration_files = None
        self._default_update_interval = 3600
        self.property_list = None

    def get(self, object_property):
        try:
            return self._data[object_property.id()]
        except:
            return None

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
        try:
            alarm_values.split(",")
        except:
            return []
