from visiobas.client import VisiobasClient
from bacnet.bacnet import ObjectType
import json
import logging


class VisiobasGateClient(VisiobasClient):
    def __init__(self, host, port, verify):
        VisiobasClient.__init__(self, host, port, verify=verify)

    def rq_get_device_objects(self, device_id: int, object_id: int = None, object_type: ObjectType = None):
        """
        Request list of object under certain device
        :param device_id: device identifier
        :type device_id: int
        :param object_id: Optional object identifier
        :type object_id: int
        :param object_type: Optional object type
        :type object_type: visiobas_object_type.ObjectType
        """
        if object_id is not None and object_type is not None:
            url = "{}/get/{}/{}/{}".format(self.get_addr(), device_id, object_id, object_type.name())
        else:
            url = "{}/get/{}".format(self.get_addr(), device_id)
        return self.get(url)

    def rq_devices(self) -> list:
        """
        Request of all available devices
        :return:
        """
        url = "{}/vbas/gate/getDevices".format(self.get_addr())
        return self.get(url)

    def rq_device_invalid_objects(self, device_id):
        """
        Return invalid objects
        :param device_id:
        :return:
        """
        url = "{}/vbas/gate/get/{}/empty".format(self.get_addr(), device_id)
        return self.get(url)

    def rq_device_object(self, device_id, object_type):
        """
        Request object
        :param device_id: device id
        :type device_id: int
        :param object_type: one of supported object type
        :type object_type: visiobas_object_type.ObjectType
        :return:
        """
        url = "{}/vbas/gate/get/{}/{}".format(self.get_addr(), device_id, object_type.id())
        return self.get(url)

    def rq_put(self, device_id, data):
        """
        :param device_id: device identifier
        :param data: list of object data to put on server
        :return:
        """
        url = "{}/vbas/gate/put/{}".format(self.get_addr(), device_id)
        headers = {
            "Content-type": "application/json;charset=UTF-8"
        }
        js = json.dumps(data)
        return self.post(url, js, headers=headers)
