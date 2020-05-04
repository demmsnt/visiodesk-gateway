import json
from bacnet.bacnet import ObjectProperty, ObjectType


class BACnetObject:
    def __init__(self, data):
        self._data = data
        self.configuration_files = None
        self._default_pooling_period = 300

    def get(self, object_property):
        try:
            return self._data[object_property.id()]
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

    def get_pooling_period(self):
        configuration = self.get_configuration_files()
        if configuration is None:
            return self._default_pooling_period
        if 'pooling_period' not in configuration:
            return self._default_pooling_period
        try:
            return int(configuration['pooling_period'])
        except:
            return self._default_pooling_period

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
