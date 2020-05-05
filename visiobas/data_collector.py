import logging
import time
import traceback
from pathlib import Path
from threading import Thread
from random import randint
from typing import Optional, Callable, Any, Iterable, Mapping
import argparse

import bacnet.config
import bacnet.config
from bacnet.bacnet import ObjectProperty, StatusFlag
from bacnet.bacnet import ObjectType
from bacnet.parser import BACnetParser
from bacnet.slicer import BACrpmSlicer
from visiobas.gate_client import VisiobasGateClient
from visiobas.object.device import Device
from visiobas.visiobas_logging import initialize_logging
from visiobas.object.bacnet_object import BACnetObject


class VisiobasTransmitter(Thread):

    def __init__(self, gate_client, period: int = 5):
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
        self.send_fields = [
            ObjectProperty.OBJECT_TYPE.id(),
            ObjectProperty.OBJECT_IDENTIFIER.id(),
            ObjectProperty.OBJECT_PROPERTY_REFERENCE.id(),
            ObjectProperty.PRESENT_VALUE.id(),
            ObjectProperty.STATUS_FLAGS.id(),
            ObjectProperty.PRIORITY_ARRAY.id()
        ]

        # how many data was send by statistic period
        self.statistic_send_object_count = 0
        self.statistic_log_period = 10
        self.statistic_send_start = time.time()
        self.statistic_period_start = time.time()

    def push_collected_data(self, data: dict):
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
                        _bacnet_object = self.collected_data.pop(_id)
                        # send only necessary fields
                        _data = {}
                        for field in self.send_fields:
                            _data[field] = _bacnet_object[field]
                        _objects.append(_data)
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


class VisiobasNotifier(Thread):
    def __init__(self,
                 client: VisiobasGateClient,
                 transmitter: VisiobasTransmitter,
                 bacnet_objects: dict):
        super().__init__()
        self.logger = logging.getLogger('visiobas.data_collector.notifier')
        self.transmitter = transmitter
        self.collected_data = {}
        self.bacnet_objects = bacnet_objects
        self.client = client
        # statistic logging
        self.statistic_verified_object_count = 0
        self.statistic_log_period = 10
        self.statistic_start = time.time()
        self.statistic_period_start = time.time()

    def push_collected_data(self, data: dict):
        try:
            id = data[ObjectProperty.OBJECT_IDENTIFIER.id()]
            self.collected_data[id] = data
            # _device_id = data[ObjectProperty.DEVICE_ID.id()]
            # if _device_id not in self.device_ids:
            #    self.device_ids.append(_device_id)
        except:
            self.logger.error("Failed put collected data: {}".format(data))
            self.logger.error(traceback.format_exc())

    def verify_analog_object_out_of_limit(self, bacnet_object: BACnetObject, data: dict):
        present_value = data[ObjectProperty.PRESENT_VALUE.id()]
        low_limit = bacnet_object.get_low_limit()
        if low_limit is not None and present_value < low_limit:
            return True
        high_limit = bacnet_object.get_high_limit()
        if high_limit is not None and present_value > high_limit:
            return True
        return False

    def verify_binary_out_of_limit(self, bacnet_object: BACnetObject, data: dict):
        present_value = data[ObjectProperty.PRESENT_VALUE.id()]
        alarm_value = bacnet_object.get_alarm_value()
        return alarm_value == present_value

    def verify_multistate_out_of_limit(self, bacnet_object: BACnetObject, data: dict):
        present_value = data[ObjectProperty.PRESENT_VALUE.id()]
        alarm_values = bacnet_object.get_alarm_values()
        return present_value in alarm_values

    def verify_if_necessary_object_out_of_limit(self, bacnet_object: BACnetObject, data: dict):
        if not bacnet_object.get_event_detection_enable():
            return False
        object_type_code = bacnet_object.get_object_type_code()
        if object_type_code == ObjectType.ANALOG_INPUT.code() or \
                object_type_code == ObjectType.ANALOG_OUTPUT.code() or \
                object_type_code == ObjectType.ANALOG_VALUE:
            return self.verify_analog_object_out_of_limit(bacnet_object, data)
        elif object_type_code == ObjectType.BINARY_INPUT.code() or \
                object_type_code == ObjectType.BINARY_OUTPUT.code() or \
                object_type == ObjectType.BINARY_VALUE.code():
            return self.verify_binary_out_of_limit(bacnet_object, data)
        elif object_type_code == ObjectType.MULTI_STATE_INPUT.code() or \
                object_type_code == ObjectType.MULTI_STATE_OUTPUT.code() or \
                object_type_code == ObjectType.MULTI_STATE_VALUE.code():
            return self.verify_multistate_out_of_limit(bacnet_object, data)

    def run(self) -> None:
        while True:
            if self.logger.isEnabledFor(logging.INFO):
                if time.time() - self.statistic_period_start > self.statistic_log_period:
                    self.statistic_period_start = time.time()
                    count = self.statistic_verified_object_count
                    rate = int(count / (time.time() - self.statistic_start))
                    self.logger.info(
                        "Statistic verify and push for transmit: {}, rate: {:d} object / sec".format(count, rate))

            ids = list(self.collected_data.keys())
            for id in ids:
                data = self.collected_data.pop(id)

                # process status flags
                # {IN_ALARM, FAULT, OVERRIDDEN, OUT_OF_SERVICE}
                # IN_ALARM logical FALSE (0) if the Event_State property has a value of NORMAL, otherwise TRUE (1)
                # FAULT logical TRUE (1) if the reliability property is present and does not have a value of NO_FAULT_DETECTED otherwise FALSE (0)
                # OVERRIDEN logical TRUE (1) if the point has been overriden by some mechanism local to the BACnet DEvice, otherwise FALSE (0)
                # OUT_OF_SERVICE logical TRUE (1) if Out_Of_Service property has a value of TRUE otherwise FALSE (0)

                if id in self.bacnet_objects:
                    bacnet_object = self.bacnet_objects[id]
                    if self.verify_if_necessary_object_out_of_limit(bacnet_object, data):
                        status_flags = StatusFlag(data[ObjectProperty.STATUS_FLAGS.id()])
                        # TODO need to verify does need to establish in_alarm flag or not?
                        status_flags.set_in_alarm(True)
                        data[ObjectProperty.STATUS_FLAGS.id()] = status_flags.as_list()
                self.transmitter.push_collected_data(data)
                self.statistic_verified_object_count += 1
            time.sleep(0.01)


class VisiobasThreadDataCollector(Thread):

    def __init__(self,
                 thread_idx: int,
                 notifier: VisiobasNotifier,
                 period: float = 0.01):
        super().__init__()
        self.thread_idx = thread_idx
        self.objects = []
        self.notifier = notifier
        # self.transmitter = transmitter
        self.logger = logging.getLogger('visiobas.data_collector.collector')
        self.period = period
        # statistic logging
        self.statistic_parsed_object_count = 0
        self.statistic_log_period = 10
        self.statistic_start = time.time()
        self.statistic_period_start = time.time()

    def add_object(self, bacnet_object: BACnetObject):
        _device_id = bacnet_object.get_device_id()
        _id = bacnet_object.get_id()
        _type_code = bacnet_object.get_object_type_code()
        _update_interval = bacnet_object.get_update_interval()
        _reference = bacnet_object.get_object_reference()
        self.objects.append({
            "device_id": _device_id,
            "object_type_code": _type_code,
            "object_id": _id,
            "object_reference": _reference,
            "update_interval": _update_interval,
            "original_update_interval": _update_interval,
            "time_last_success_pooling": 0,
            # special delay for make uniform distribute of sensors pooling
            "update_delay": -1,
            "bacnet_object": bacnet_object
        })

    # def add_object(self, device_id, object_type_code, object_id, update_interval=3600, object_reference=None):
    #     # python list append operation should be thread safe
    #     self.objects.append({
    #         "device_id": device_id,
    #         "object_type_code": object_type_code,
    #         "object_id": object_id,
    #         "object_reference": object_reference,
    #         "update_interval": update_interval,
    #         "original_update_interval": update_interval,
    #         "time_last_success_pooling": 0,
    #         # special delay for distribute sensor pooling uniform
    #         "update_delay": -1
    #     })

    def run(self):
        if self.logger.isEnabledFor(logging.INFO):
            self.logger.info("Collector# {} count of observable objects: {}".format(self.thread_idx, len(self.objects)))
        while True:
            if self.logger.isEnabledFor(logging.INFO):
                if time.time() - self.statistic_period_start > self.statistic_log_period:
                    self.statistic_period_start = time.time()
                    count = self.statistic_parsed_object_count
                    rate = int(count / (time.time() - self.statistic_start))
                    self.logger.info(
                        "Statistic parsed and push for verification: {}, rate: {:d} object / sec".format(count, rate))

            slicer = BACrpmSlicer(bacnet.config.bacrmp_app_path)
            now = time.time()
            for _object in self.objects:
                try:
                    time_last_success_pooling = _object["time_last_success_pooling"]
                    update_delay = _object["update_delay"]
                    update_interval = _object["update_interval"]
                    device_id = _object["device_id"]
                    object_type_code = _object["object_type_code"]
                    object_id = _object["object_id"]
                    object_reference = _object["object_reference"]
                    fields = [
                        ObjectProperty.OUT_OF_SERVICE.id(),
                        ObjectProperty.PRESENT_VALUE.id(),
                        ObjectProperty.RELIABILITY.id(),
                        ObjectProperty.STATUS_FLAGS.id(),
                        ObjectProperty.PRIORITY_ARRAY.id()
                    ]

                    if now - time_last_success_pooling > update_interval:
                        # make sensor pooling distributed more uniformed
                        _object["update_delay"] = randint(1, max(int(update_interval), 1)) \
                            if update_delay == -1 else 0
                        _object["update_interval"] = _object["update_delay"] \
                            if _object["update_delay"] > 0 else _object["original_update_interval"]

                        data = slicer.execute(device_id, object_type_code, object_id, fields)
                        _object["time_last_success_pooling"] = time.time()
                        # prepare collected data and store to be transmitted to server
                        if object_reference is not None:
                            data[ObjectProperty.OBJECT_PROPERTY_REFERENCE.id()] = object_reference
                        # convert present value to float
                        if object_type_code == ObjectType.ANALOG_INPUT.code() or \
                                object_type_code == ObjectType.ANALOG_OUTPUT.code() or \
                                object_type_code == ObjectType.ANALOG_VALUE.code():
                            data[ObjectProperty.PRESENT_VALUE.id()] = float(data[ObjectProperty.PRESENT_VALUE.id()])
                        # convert present value to int
                        if object_type_code == ObjectType.MULTI_STATE_INPUT.code() or \
                                object_type_code == ObjectType.MULTI_STATE_OUTPUT.code() or \
                                object_type_code == ObjectType.MULTI_STATE_VALUE.code():
                            data[ObjectProperty.PRESENT_VALUE.id()] = int(
                                float(data[ObjectProperty.PRESENT_VALUE.id()]))
                        # binary present value without changes actually it 'active' or 'inactive'
                        data[ObjectProperty.OBJECT_IDENTIFIER.id()] = object_id
                        data[ObjectProperty.DEVICE_ID.id()] = device_id
                        data[ObjectProperty.OBJECT_TYPE.id()] = ObjectType.code_to_name(object_type_code)
                        # object (data) ready to transmit to server side
                        # transmitter.push_collected_data(data, _object["bacnet_object"])
                        self.notifier.push_collected_data(data)
                        self.statistic_parsed_object_count += 1
                except:
                    logger.error(traceback.format_exc())
            time.sleep(self.period)


# entry point of data_collector
if __name__ == '__main__':
    initialize_logging()
    logger = logging.getLogger('visiobas.data_collector')
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--device", type=int)
    argparser.add_argument("--object", type=int)
    args = argparser.parse_args()

    address_cache_path = bacnet.config.address_cache_path
    if not Path(address_cache_path).is_file():
        logger.error("File 'address_cache' not found: {}".format(address_cache_path))
        exit(0)

    try:
        address_cache = Path(address_cache_path).read_text()
        address_cache_devices = BACnetParser.parse_bacwi(address_cache)
        device_ids = [x['id'] for x in address_cache_devices]

        # dict of all collecting bacnet objects
        # key - object id, value - BACnetObject
        bacnet_objects = {}

        client = VisiobasGateClient(
            bacnet.config.visiobas_server['host'],
            bacnet.config.visiobas_server['port'],
            bacnet.config.visiobas_server['ssl_verify'])

        try:
            # how often need to perform login ?
            client.rq_login(bacnet.config.visiobas_server['auth']['user'],
                            bacnet.config.visiobas_server['auth']['pwd'])

            # get notification class objects
            notification_class = client.rq_device_object(1, ObjectType.NOTIFICATION_CLASS)
            for o in notification_class:
                bacnet_objects[o[ObjectProperty.OBJECT_IDENTIFIER.id()]] = BACnetObject(o)

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
                if 'device' in args:
                    if not args.device == _device_id:
                        continue

                host = address_cache_device['host']
                port = address_cache_device['port']
                server_device = None
                for device in server_devices:
                    if device[ObjectProperty.OBJECT_IDENTIFIER.id()] == _device_id:
                        server_device = device
                        break
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

            notifier = VisiobasNotifier(client, transmitter, bacnet_objects)
            notifier.setDaemon(True)
            notifier.start()

            # list of object types for collect
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
                _devices = port_devices[port]
                data_collector_objects = []
                for device in _devices:
                    for object_type in object_types:
                        objects = client.rq_device_object(device.get_id(), object_type)
                        if logger.isEnabledFor(logging.DEBUG):
                            object_ids = [x[ObjectProperty.OBJECT_IDENTIFIER.id()] for x in objects]
                            logger.debug(
                                "Collector# {} device: {} type: {} objects: {}".format(thread_idx,
                                                                                       device.get_id(),
                                                                                       object_type,
                                                                                       object_ids))

                        if 'object' in args:
                            objects = list(filter(
                                lambda x: x[ObjectProperty.OBJECT_IDENTIFIER.id()] == args.object, objects))

                        # collect map of bacnet object and link reference with notification class object
                        for o in objects:
                            bacnet_object = BACnetObject(o)
                            notification_class = bacnet_object.get_notification_class()
                            if not notification_class == 0 and notification_class in bacnet_objects:
                                bacnet_object.set_notification_object(notification_class)
                            bacnet_objects[o[ObjectProperty.OBJECT_IDENTIFIER.id()]] = bacnet_object
                        data_collector_objects += objects

                collector = VisiobasThreadDataCollector(thread_idx, notifier)
                if logger.isEnabledFor(logging.INFO):
                    _device_ids = [x.get_id() for x in _devices]
                    logger.info("Collector# {} collect devices: {}".format(thread_idx, _device_ids))
                for o in data_collector_objects:
                    bacnet_object = BACnetObject(o)
                    collector.add_object(bacnet_object)
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
