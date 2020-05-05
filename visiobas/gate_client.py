from visiobas.client import VisiobasClient
from bacnet.bacnet import ObjectType
import json
import logging


# TODO why need VisiobasClient or VisiobasGateClient ? move all into VisiobasClient
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

    def rq_device_object(self, device_id: int, object_type: ObjectType):
        """
        Request object
        :param device_id: device id
        :param object_type: one of supported object type
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

    def rq_vdesk_get_status_list(self) -> list:
        url = "{}/vdesk/arm/getStatusList".format(self.get_addr())
        return self.get_json(url)

    def rq_vdesk_get_priorities(self) -> list:
        url = "{}/vdesk/arm/getPriorities".format(self.get_addr())
        return self.get_json(url)

    def rq_vdesk_get_support_levels(self) -> list:
        url = "{}/vdesk/arm/getSupportLevels".format(self.get_addr())
        return self.get_json(url)

    def rq_vdesk_get_user_types(self):
        url = "{}/vdesk/arm/getUserTypes".format(self.get_addr())
        return self.get_json(url)

    def rq_vdesk_get_topic_type_items(self):
        url = "{}/vdesk/arm/getTopicItemTypes".format(self.get_addr())
        return self.get_json(url)

    def rq_vdesk_get_topic_types(self):
        url = "{}/vdesk/arm/getTopicTypes".format(self.get_addr())
        return self.get_json(url)

    def rq_vdesk_get_groups(self):
        url = "{}/vdesk/arm/getGroups".format(self.get_addr())
        return self.get_json(url)

    def rq_vdesk_get_users_by_group(self):
        # TODO not work
        url = "{}/vdesk/arm/getUsersByGroup".format(self.get_addr())
        return self.get_json(url)

    def rq_vdesk_get_users(self):
        url = "{}/vdesk/arm/getUsers".format(self.get_addr())
        return self.get_json(url)

    def rq_vdesk_get_user_by_id(self, user_id: int):
        url = "{}/vdesk/arm/getUserById".format(self.get_addr())
        headers = {
            "Content-type": "application/json;charset=UTF-8",
            "X-ID": user_id
        }
        return self.get(url, headers=headers)

    def rq_vdesk_add_topic_item(self, data):
        url = "{}/vdesk/arm/addTopicItem".format(self.get_addr())
        headers = {
            "Content-type": "application/json;charset=UTF-8",
        }
        return self.post(url, data, headers=headers)
