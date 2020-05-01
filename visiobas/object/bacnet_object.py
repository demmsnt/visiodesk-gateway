from bacnet.bacnet import ObjectProperty


class BACnetObject:
    def __init__(self, data):
        self._data = data

    def get(self, object_property):
        try:
            return self._data[object_property.id()]
        except:
            return None

    def get_id(self):
        return self.get(ObjectProperty.OBJECT_IDENTIFIER)
