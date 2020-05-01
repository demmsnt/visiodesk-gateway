import argparse
import logging
import traceback
import time
from pathlib import Path

import bacnet.config
from threading import Thread
from bacnet.slicer import BACrpmSlicer
from visiobas.object.device import Device
from visiobas.visiobas_logging import initialize_logging
from visiobas.gate_client import VisiobasGateClient
import bacnet.config
from bacnet.bacnet import ObjectProperty
from bacnet.bacnet import ObjectType
from bacnet.parser import BACnetParser


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
    initialize_logging()
    logger = logging.getLogger(__name__)

    address_cache_path = bacnet.config.address_cache_path
    if not Path(address_cache_path).is_file():
        logger.error("File 'address_cache' not found: {}".format(address_cache_path))
        exit(0)

    try:
        address_cache = Path(address_cache_path).read_text()
        address_cache_devices = BACnetParser.parse_bacwi(address_cache)
        device_ids = [x['id'] for x in address_cache_devices]

        client = VisiobasGateClient(
            bacnet.config.visiobas_server['host'],
            bacnet.config.visiobas_server['port'],
            bacnet.config.visiobas_server['ssl_verify'])
        try:
            # how often need to perform login ?
            client.rq_login(bacnet.config.visiobas_server['auth']['user'],
                            bacnet.config.visiobas_server['auth']['pwd'])

            server_devices = client.rq_devices()
            server_devices = filter(lambda x: x[ObjectProperty.OBJECT_IDENTIFIER.id()] in device_id, server_devices)
            if not len(device_ids) == len(server_devices):
                logger.warning("Not all bacwi table devices exist on server")
                for address_cache_device in address_cache_devices:
                    device_id = address_cache_device['id']
                    found = next((x for x in server_devices
                                  if lambda d: d[ObjectProperty.OBJECT_IDENTIFIER.id()] == device_id), None)
                    if found is None:
                        logger.warning("Device not found on server side: {}".format(address_cache_device))

            port_devices = {}
            # group devices by port value
            # devices with different port value can be collected independently
            for address_cache_device in address_cache_devices:
                device_id = address_cache_device['id']
                host = address_cache_device['host']
                port = address_cache_device['port']
                server_device = next((x for x in server_devices
                                      if lambda d: d[ObjectProperty.OBJECT_IDENTIFIER.id()] == device_id), None)
                if server_device is None:
                    continue

                # verify host and port equals on server device and bacwi device table
                server_device = Device(server_device)
                if not host == server_device.get_host():
                    logger.warning("Server device {} host ({}) not equal with bacwi device host ({})".
                                   format(server_device.get_id(), server_device.get_host(), host))
                if not port == server_device.get_port():
                    logger.warning("Server device {} port ({}) not equal with bacwi device port ({})"
                                   .format(server_device.get_id(), server_device.get_port(), port))

                if port not in port_devices:
                    port_devices[port] = []
                else:
                    port_devices[port].append(server_device)

            thread_count = len(port_devices)

            transmitter = VisiobasTransmitter(client)
            transmitter.setDaemon(True)
            transmitter.start()

            object_types = [
                ObjectType.ANALOG_INPUT,
                ObjectType.ANALOG_OUTPUT,
                ObjectType.ANALOG_VALUE,
                ObjectType.BINARY_INPUT,
                ObjectType.BINARY_OUTPUT,
                ObjectType.BINARY_VALUE,
                ObjectType.MULTI_STATE_INPUT,
                ObjectType.MULTI_STATE_OUTPUT,
                ObjectType.MULTI_STATE_VALUE
            ]

            collectors = []
            thread_idx = 1
            for devices in port_devices:
                data_collector_objects = []
                for device in devices:
                    for object_type in object_types:
                        objects = client.rq_device_object(device.get_id(), object_type)
                        if logger.isEnabledFor(logging.DEBUG):
                            object_ids = [x[ObjectProperty.OBJECT_IDENTIFIER.id()] for x in objects]
                            logger.debug("Collector thread# {} object: {}".format(thread_idx, object_ids))
                        data_collector_objects += objects

                collector = VisiobasThreadDataCollector(transmitter)
                for o in data_collector_objects:
                    collector.add_object(
                        o[ObjectProperty.DEVICE_ID.id()],
                        o[ObjectProperty.OBJECT_TYPE.id()],
                        o[ObjectProperty.OBJECT_IDENTIFIER.id()],
                        5,
                        o[ObjectProperty.OBJECT_PROPERTY_REFERENCE.id()])
                collector.start()
                collectors.append(collector)
                thread_idx += 1

            # wait until all collector stop threads
            for collector in collectors:
                collector.join()
        except BaseException as e:
            client.rq_logout()
            raise e
    except BaseException as e:
        logger.error(traceback.format_exc())

    # data_collector2 = VisiobasThreadDataCollector(transmitter)
    # data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5,
    #                            object_reference="Site:Blok_A/ITP.AI_25307")
    # data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5,
    #                            object_reference="Site:Blok_A/ITP.AI_25307")
    # data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5,
    #                            object_reference="Site:Blok_A/ITP.AI_25307")
    # data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5,
    #                            object_reference="Site:Blok_A/ITP.AI_25307")
    # data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5,
    #                            object_reference="Site:Blok_A/ITP.AI_25307")
    # data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5,
    #                            object_reference="Site:Blok_A/ITP.AI_25307")
    # data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5,
    #                            object_reference="Site:Blok_A/ITP.AI_25307")
    # data_collector2.start()
    # data_collector2.join()
    #
    # data_collector2 = VisiobasThreadDataCollector(transmitter)
    # data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5,
    #                            object_reference="Site:Blok_A/ITP.AI_25307")
    # data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5,
    #                            object_reference="Site:Blok_A/ITP.AI_25307")
    # data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5,
    #                            object_reference="Site:Blok_A/ITP.AI_25307")
    # data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5,
    #                            object_reference="Site:Blok_A/ITP.AI_25307")
    # data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5,
    #                            object_reference="Site:Blok_A/ITP.AI_25307")
    # data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5,
    #                            object_reference="Site:Blok_A/ITP.AI_25307")
    # data_collector2.add_object(200, ObjectType.ANALOG_INPUT.code(), 25307, 5,
    #                            object_reference="Site:Blok_A/ITP.AI_25307")
    # data_collector2.start()
    # data_collector2.join()
