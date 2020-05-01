from threading import Thread
from bacnet.slicer import BACrpmSlicer
import logging
import bacnet.config
import time
import visiobas.visiobas_logging
from visiobas.gate_client import VisiobasGateClient
import bacnet.config
from bacnet.bacnet import ObjectProperty
from bacnet.bacnet import ObjectType


class VisiobasTransmitter(Thread):

    def __init__(self, gate_client):
        super().__init__()
        # global collected data should be transmitted to server
        self.collected_data = []
        self.gate_client = gate_client
        self.logger = logging.getLogger(__name__)

    def push_collected_data(self, data):
        self.collected_data.append(data)

    def run(self) -> None:
        while True:
            if len(self.collected_data) > 0:
                data = self.collected_data.pop()
                # TODO collect batch data into one request group by device id
                # replace old data
                request = [data]
                try:
                    self.gate_client.rq_put(data[ObjectProperty.DEVICE_ID.id()], request)
                except Exception as e:
                    self.logger.error("Failed put data: {}".format(e))
                    self.logger.error("Failed put data: {}".format(request))
            time.sleep(1)


class VisiobasThreadDataCollector(Thread):

    def __init__(self, transmitter):
        super().__init__()
        self.objects = []
        self.transmitter = transmitter

    def add_object(self, device_id, object_type_code, object_id, slice_period=1, object_reference=None):
        # python list append operation should be thread safe
        self.objects.append({
            "device_id": device_id,
            "object_type_code": object_type_code,
            "object_id": object_id,
            "object_reference": object_reference,
            "slice_period": slice_period,
            "time_last_success_slice": 0
        })

    def run(self):
        while True:
            slicer = BACrpmSlicer(bacnet.config.bacrmp_app_path)
            now = time.time()
            for object in self.objects:
                time_last_success_slice = object["time_last_success_slice"]
                slice_period = object["slice_period"]
                device_id = object["device_id"]
                object_type_code = object["object_type_code"]
                object_id = object["object_id"]
                object_reference = object["object_reference"]
                fields = [
                    ObjectProperty.OBJECT_IDENTIFIER.id(),
                    ObjectProperty.OBJECT_PROPERTY_REFERENCE.id(),
                    ObjectProperty.OBJECT_TYPE.id(),
                    ObjectProperty.OUT_OF_SERVICE.id(),
                    ObjectProperty.PRESENT_VALUE.id(),
                    ObjectProperty.RELIABILITY.id(),
                    ObjectProperty.STATUS_FLAGS.id(),
                    ObjectProperty.SYSTEM_STATUS.id()
                ]
                if now - time_last_success_slice > slice_period:
                    data = slicer.execute(device_id, object_type_code, object_id, fields)
                    object["time_last_success_slice"] = time.time()
                    # prepare collected data and store to be transmitted to server
                    if object_reference is not None:
                        data[ObjectProperty.OBJECT_PROPERTY_REFERENCE.id()] = object_reference
                    if ObjectProperty.OBJECT_IDENTIFIER.id() in data:
                        data[ObjectProperty.OBJECT_IDENTIFIER.id()] = int(data[ObjectProperty.OBJECT_IDENTIFIER.id()])
                    if object_type_code == ObjectType.ANALOG_INPUT.code() or \
                            object_type_code == ObjectType.ANALOG_OUTPUT.code() or \
                            object_type_code == ObjectType.ANALOG_VALUE.code():
                        data[ObjectProperty.PRESENT_VALUE.id()] = float(data[ObjectProperty.PRESENT_VALUE.id()])
                    data[ObjectProperty.DEVICE_ID.id()] = device_id
                    transmitter.push_collected_data(data)
            time.sleep(1)

# TODO remove main move test_visiobas into unit test_visiobas
if __name__ == '__main__':
    visiobas.visiobas_logging.initialize_logging()

    gate_client = VisiobasGateClient(
        bacnet.config.visiobas_server_host,
        bacnet.config.visiobas_server_port,
        verify=True)
    # describe how to control return value
    rs = gate_client.rq_login("s.gubarev", "77777")

    transmitter = VisiobasTransmitter(gate_client)
    transmitter.setDaemon(True)
    transmitter.start()

    data_collector2 = VisiobasThreadDataCollector(transmitter)
    data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5, object_reference="Site:Blok_A/ITP.AI_25307")
    data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5, object_reference="Site:Blok_A/ITP.AI_25307")
    data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5, object_reference="Site:Blok_A/ITP.AI_25307")
    data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5, object_reference="Site:Blok_A/ITP.AI_25307")
    data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5, object_reference="Site:Blok_A/ITP.AI_25307")
    data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5, object_reference="Site:Blok_A/ITP.AI_25307")
    data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5, object_reference="Site:Blok_A/ITP.AI_25307")
    data_collector2.start()
    data_collector2.join()


    data_collector2 = VisiobasThreadDataCollector(transmitter)
    data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5, object_reference="Site:Blok_A/ITP.AI_25307")
    data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5, object_reference="Site:Blok_A/ITP.AI_25307")
    data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5, object_reference="Site:Blok_A/ITP.AI_25307")
    data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5, object_reference="Site:Blok_A/ITP.AI_25307")
    data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5, object_reference="Site:Blok_A/ITP.AI_25307")
    data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5, object_reference="Site:Blok_A/ITP.AI_25307")
    data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5, object_reference="Site:Blok_A/ITP.AI_25307")
    data_collector2.start()
    data_collector2.join()
