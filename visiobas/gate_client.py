from visiobas.client import VisiobasClient
from bacnet.bacnet import ObjectType
import json
import logging
import re


# TODO why need VisiobasClient or VisiobasGateClient ? move all into VisiobasClient
class VisiobasGateClient(VisiobasClient):
    def __init__(self, host, port, verify, login=None, md5_pwd=None, write_put_requests=0):
        VisiobasClient.__init__(self, host, port, verify=verify, login=login, md5_pwd=md5_pwd)
        self.write_put_requests = write_put_requests

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
        url = "{}/vbas/gate/get/{}/{}".format(self.get_addr(), device_id, object_type.name())
        return self.get(url)

    def rq_put(self, device_id, data):
        """
        :param device_id: device identifier
        :param data: list of object data to put on server
        :return: list of rejected data
        """
        url = "{}/vbas/gate/put/{}".format(self.get_addr(), device_id)
        headers = {
            "Content-type": "application/json;charset=UTF-8"
        }
        js = json.dumps(data)
        if self.write_put_requests == 1:
            with open("logs/put_request.txt", "a+") as f:
                f.write("{}\n".format(js))
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
        # TODO not work?
        url = "{}/vdesk/arm/getUsersByGroup".format(self.get_addr())
        return self.get_json(url)

    def rq_vdesk_get_users(self):
        url = "{}/vdesk/arm/getUsers".format(self.get_addr())
        return self.get_json(url)

    def rq_vdesk_get_user_by_id(self, user_id: int):
        # TODO not work?
        url = "{}/vdesk/arm/getUserById".format(self.get_addr())
        headers = {
            "Content-type": "application/json;charset=UTF-8",
            "X-ID": user_id
        }
        return self.get(url, headers=headers)

    # def rq_vdesk_add_topic_item(self, data):
    #     url = "{}/vdesk/arm/addTopicItem".format(self.get_addr())
    #     headers = {
    #         "Content-type": "application/json;charset=UTF-8",
    #     }
    #     js = json.dumps(data)
    #     return self.post(url, js, headers=headers)

    def rq_vdesk_add_topic(self, data):
        url = "{}/vdesk/arm/addTopic".format(self.get_addr())
        headers = {
            "Content-type": "application/json;charset=UTF-8",
        }
        js = json.dumps(data)
        return self.post(url, js, headers=headers)

    def rq_vdesk_get_topic_by_user(self, user_id: int = None):
        url = "{}/vdesk/arm/getTopicsByUser".format(self.get_addr())
        headers = {
            "Content-type": "application/json;charset=UTF-8",
        }
        if user_id is not None:
            headers["X-ID"] = user_id
        return self.get(url, headers=headers)

    def rq_vdesk_add_topic_items(self, data):
        url = "{}/vdesk/arm/addTopicItems".format(self.get_addr())
        headers = {
            "Content-type": "application/json;charset=UTF-8",
        }
        js = json.dumps(data)
        return self.post(url, js, headers=headers)

    def rq_vdesk_get_topic_by_id(self, topic_id: int):
        url = "{}/vdesk/arm/getTopicById/{}".format(self.get_addr(), topic_id)
        return self.get_json(url)

    def __convert_to_url_reference(self, reference: str):
        return "/".join(self.reference_as_list(reference))

    @staticmethod
    def reference_as_list(reference: str):
        return re.split("[:.]", reference)

    def rq_vbas_get_object(self, reference: str):
        url = "{}/vbas/arm/getObject/{}".format(self.get_addr(), self.__convert_to_url_reference(reference))
        return self.get_json(url)
