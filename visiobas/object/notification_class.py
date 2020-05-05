from visiobas.object.bacnet_object import BACnetObject
from bacnet.bacnet import ObjectProperty


class NotificationClass(BACnetObject):
    def __init__(self, data):
        super().__init__(data)

    def get_recipient_list(self):
        recipient_list = self.get(ObjectProperty.RECIPIENT_LIST)
        return recipient_list if type(recipient_list) is list else []
