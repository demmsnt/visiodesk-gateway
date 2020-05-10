from bacnet.bacnet import ObjectType
from bacnet.bacnet import ObjectProperty
from visiobas.object.bacnet_object import BACnetObject
from visiobas.object.bacnet_object import Device
from visiobas.object.bacnet_object import NotificationClass


class BACnetNetwork:

    def __init__(self) -> None:
        super().__init__()
        self.objects = {}
        self.map_reference = {
            ObjectType.DEVICE.code(): {}
        }

    def find(self, reference: str, ):
        key = self.__create_key(reference)
        if key in self.objects:
            return self.objects[key]
        return None

    def find_by_type(self, object_type, object_id):
        object_type_code = object_type.code() if type(object_type) == ObjectType else object_type
        if object_type_code == ObjectType.DEVICE.code():
            devices = self.map_reference[ObjectType.DEVICE.code()]
            if object_id in devices:
                return self.find(devices[object_id])
        for k in self.objects:
            bacnet_object = self.objects[k]
            if bacnet_object.get_object_type_code() == object_type_code and bacnet_object.get_id() == object_id:
                return bacnet_object
        return None

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
            object_type_code = o.get_object_type_code()
            # group some object for improve searching
            if object_type_code == ObjectType.DEVICE.code():
                self.map_reference[ObjectType.DEVICE.code()][o.get_id()] = o.get_object_reference()
            self.objects[self.__create_key(o.get_object_reference())] = o

    def __create_key(self, reference):
        return reference
        # if type(object_type) == ObjectType:
        #     object_type = object_type.code()
        # return str(object_type) + "_" + str(object_id)

    def save(self, file):
        with open(file, "+w") as file:
            for k in self.objects:
                bacnet_object = self.objects[k]
                file.write("{}\n".format(str(bacnet_object)))
