import logging
import time
import traceback
from pathlib import Path
from threading import Thread

import bacnet.config
import bacnet.config
from bacnet.bacnet import ObjectProperty
from bacnet.bacnet import ObjectType
from bacnet.parser import BACnetParser
from bacnet.slicer import BACrpmSlicer
from visiobas.gate_client import VisiobasGateClient
from visiobas.object.device import Device
from visiobas.visiobas_logging import initialize_logging


class VisiobasTransmitter(Thread):

    def __init__(self, gate_client, period: int = 1):
        """
        :param gate_client:
        :param period: time in seconds waiting new data before send collected data to server
        """
        super().__init__()
        # global collected data should be transmitted to server
        self.device_ids = []
        self.collected_data = {}
        self.gate_client = gate_client
        self.period = period
        self.logger = logging.getLogger('visiobas.data_collector.transmitter')
        # how many data was send by statistic period
        self.statistic_send_object_count = 0
        self.statistic_log_period = 10
        self.statistic_send_start = time.time()
        self.statistic_period_start = time.time()

    def push_collected_data(self, data):
        try:
            _id = data[ObjectProperty.OBJECT_IDENTIFIER.id()]
            _device_id = data[ObjectProperty.DEVICE_ID.id()]
            self.collected_data[_id] = data
            if _device_id not in self.device_ids:
                self.device_ids.append(_device_id)
        except:
            self.logger.error("Failed put collected data: {}".format(data))
            self.logger.error(traceback.format_exc())

    def run(self) -> None:
        while True:
            if self.logger.isEnabledFor(logging.INFO):
                if time.time() - self.statistic_period_start > self.statistic_log_period:
                    self.statistic_period_start = time.time()
                    count = self.statistic_send_object_count
                    rate = int(count / (time.time() - self.statistic_send_start))
                    self.logger.info("Statistic send object: {}, rate: {:d} object / sec".format(count, rate))
            if len(self.collected_data) == 0:
                continue
            if len(self.device_ids) == 0:
                continue
            if self.logger.isEnabledFor(logging.DEBUG):
                logger.debug("Prepare collected data size: {} of devices: {} for sending".format(
                    len(self.collected_data), self.device_ids))
            _device_ids = self.device_ids.copy()
            # iterate over all object devices to be able to send all different device objects
            while _device_ids:
                _device_id = _device_ids.pop()
                object_ids_group_by_device = list(
                    filter(lambda _id: self.collected_data[_id][ObjectProperty.DEVICE_ID.id()] == _device_id,
                           self.collected_data))
                # remove from collected data grouped devices
                _objects = []
                for _id in object_ids_group_by_device:
                    try:
                        _objects.append(self.collected_data.pop(_id))
                    except:
                        self.logger.error(traceback.format_exc())
                request = _objects
                try:
                    self.gate_client.rq_put(_device_id, request)
                except Exception as e:
                    self.logger.error("Failed put data: {}".format(e))
                    self.logger.error("Failed put data: {}".format(request))
                self.statistic_send_object_count += len(_objects)

            time.sleep(self.period)


class VisiobasThreadDataCollector(Thread):

    def __init__(self, thread_idx, transmitter, period: float = 0.01):
        """
        :param transmitter:
        :param period: time delay between next data collect iteration
        """
        super().__init__()
        self.thread_idx = thread_idx
        self.objects = []
        self.transmitter = transmitter
        self.logger = logging.getLogger('visiobas.data_collector.collector')
        self.period = period

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
        if self.logger.isEnabledFor(logging.INFO):
            self.logger.info("Collector# {} count of observable objects: {}".format(self.thread_idx, len(self.objects)))
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
                    # object (data) ready to transmit to server side
                    transmitter.push_collected_data(data)
            time.sleep(self.period)


# entry point of data_collector
if __name__ == '__main__':
    initialize_logging()
    logger = logging.getLogger('visiobas.data_collector')

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
            server_devices = list(
                filter(lambda x: x[ObjectProperty.OBJECT_IDENTIFIER.id()] in device_ids, server_devices))
            if not len(device_ids) == len(server_devices):
                logger.warning("Not all bacwi table devices exist on server")
                for address_cache_device in address_cache_devices:
                    _device_id = address_cache_device['id']
                    found = next((x for x in server_devices
                                  if lambda d: d[ObjectProperty.OBJECT_IDENTIFIER.id()] == _device_id), None)
                    if found is None:
                        logger.warning("Device not found on server side: {}".format(address_cache_device))

            port_devices = {}
            # group devices by port value
            # devices with different port value can be collected independently
            for address_cache_device in address_cache_devices:
                _device_id = address_cache_device['id']
                host = address_cache_device['host']
                port = address_cache_device['port']
                server_device = None
                for device in server_devices:
                    if device[ObjectProperty.OBJECT_IDENTIFIER.id()] == _device_id:
                        server_device = device
                        break
                # server_device = next((x for x in server_devices
                #                       if lambda d: d[ObjectProperty.OBJECT_IDENTIFIER.id()] == _device_id), None)
                if server_device is None:
                    continue

                # verify host and port equals on server device and bacwi device table
                server_device = Device(server_device)
                if not host == server_device.get_host():
                    logger.warning("Server device {} host ({}) not equal with bacwi device host ({})".
                                   format(server_device.get_id(), server_device.get_host(), host))
                    logger.warning("Using bacwi host value for data collection.\n\
                                   Too resolve this issue update bacwi table or update server host value")
                    server_device.set_host(host)
                if not port == server_device.get_port():
                    logger.warning("Server device {} port ({}) not equal with bacwi device port ({})"
                                   .format(server_device.get_id(), server_device.get_port(), port))
                    logger.warning("Using bacwi port value for data collection.\n\
                                   Too resolve this issue update bacwi table or update server port value")
                    server_device.set_port(port)

                if port not in port_devices:
                    port_devices[port] = []
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
            for port in port_devices:
                devices = port_devices[port]
                data_collector_objects = []
                for device in devices:
                    for object_type in object_types:
                        objects = client.rq_device_object(device.get_id(), object_type)
                        if logger.isEnabledFor(logging.DEBUG):
                            object_ids = [x[ObjectProperty.OBJECT_IDENTIFIER.id()] for x in objects]
                            logger.debug(
                                "Collector thread# {} device: {} type: {} objects: {}".format(thread_idx,
                                                                                              device.get_id(),
                                                                                              object_type,
                                                                                              object_ids))
                        data_collector_objects += objects

                collector = VisiobasThreadDataCollector(thread_idx, transmitter)
                for o in data_collector_objects:
                    _device_id = o[ObjectProperty.DEVICE_ID.id()]
                    _id = o[ObjectProperty.OBJECT_IDENTIFIER.id()]
                    _type_code = ObjectType.name_to_code(o[ObjectProperty.OBJECT_TYPE.id()])
                    _period = 5
                    _reference = o[ObjectProperty.OBJECT_PROPERTY_REFERENCE.id()]

                    collector.add_object(
                        _device_id,
                        _type_code,
                        _id,
                        _period,
                        _reference)
                collector.start()
                collectors.append(collector)
                thread_idx += 1

            # wait until all collector stop threads
            for collector in collectors:
                collector.join()
        except BaseException as e:
            client.rq_logout()
            raise e
    except:
        logger.error(traceback.format_exc())
