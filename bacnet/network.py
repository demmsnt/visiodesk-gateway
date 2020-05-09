from bacnet.bacnet import ObjectType
from bacnet.bacnet import ObjectProperty
from visiobas.object.bacnet_object import BACnetObject
from visiobas.object.bacnet_object import Device
from visiobas.object.bacnet_object import NotificationClass


class BACnetNetwork:

    def __init__(self) -> None:
        super().__init__()
        self.objects = {}

    def find(self, object_type, object_id):
        key = self.__create_key(object_type, object_id)
        if key in self.objects:
            return self.objects[key]
        return None

    def exist(self, object_type, object_id):
        return self.find(object_type, object_id) is not None

    def append(self, o):
        if type(o) == dict:
            object_type = o[ObjectProperty.OBJECT_TYPE.id()]
            if object_type == ObjectType.DEVICE.name():
                self.append(Device(o))
            elif object_type == ObjectType.NOTIFICATION_CLASS.name():
                self.append(NotificationClass(o))
            else:
                self.append(BACnetObject(o))
        elif type(o) == BACnetObject or BACnetObject in type(o).__bases__:
            self.objects[self.__create_key(o.get_object_type_code(), o.get_id())] = o

    def __create_key(self, object_type, object_id):
        if type(object_type) == ObjectType:
            object_type = object_type.code()
        return str(object_type) + str(object_id)
