import json

from bacnet.bacnet import ObjectProperty


class Device:
    def __init__(self, data):
        self._data = data
        self.property_list = None
        self.configuration_files = None

    def __get_property(self, property):
        try:
            return self._data[property]
        except:
            return None

    def get_property_list(self):
        if self.property_list is not None:
            return self.property_list
        else:
            try:
                self.property_list = json.loads(self.__get_property(ObjectProperty.PROPERTY_LIST.id()))
                return self.property_list
            except:
                return None

    def get_configuration_files(self):
        if self.configuration_files is not None:
            return self.configuration_files
        else:
            try:
                self.configuration_files = json.loads(self.__get_property(ObjectProperty.CONFIGURATION_FILES.id()))
                return self.configuration_files
            except:
                return None

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
