import json

from bacnet.bacnet import ObjectProperty
from visiobas.object.bacnet_object import BACnetObject


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
