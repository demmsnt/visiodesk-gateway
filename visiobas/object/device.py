import json

from bacnet.bacnet import ObjectProperty
from visiobas.object.bacnet_object import BACnetObject


class Device(BACnetObject):
    def __init__(self, data):
        super().__init__(data)
        self.property_list = None
        self.configuration_files = None

    def get_property_list(self):
        if self.property_list is not None:
            return self.property_list
        else:
            try:
                self.property_list = json.loads(self.get(ObjectProperty.PROPERTY_LIST))
                return self.property_list
            except:
                return None

    def get_configuration_files(self):
        if self.configuration_files is not None:
            return self.configuration_files
        else:
            try:
                self.configuration_files = json.loads(self.get(ObjectProperty.CONFIGURATION_FILES))
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
