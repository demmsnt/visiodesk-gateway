from threading import Thread
from bacnet.slicer import BACrpmSlicer
import logging
import bacnet.config
import time
import visiobas.visiobas_logging
from visiobas.gate_client import VisiobasGateClient
import bacnet.config
from bacnet.bacnet import ObjectProperty


class VisiobasTransmitter(Thread):

    def __init__(self):
        super().__init__()
        # global collected data should be transmitted to server
        self.collected_data = []
        self.gate_client = VisiobasGateClient(
            bacnet.config.visiobas_server_host,
            bacnet.config.visiobas_server_port,
            verify=True)
        self.logger = logging.getLogger(__name__)

    def push_collected_data(self, data):
        self.collected_data.append(data)

    def run(self) -> None:
        while True:
            if len(self.collected_data) > 0:
                data = self.collected_data.pop()
                try:
                    self.gate_client.rq_put(data[ObjectProperty.DEVICE_ID.id()], data)
                except Exception as e:
                    self.logger.error("Faile put data: {}".format(e))
                    self.logger.error("Failed put data: {}".format(data))
            time.sleep(1)


class VisiobasThreadDataCollector(Thread):

    def __init__(self, transmitter):
        super().__init__()
        self.objects = []
        self.transmitter = transmitter

    def add_object(self, device_id, object_id, slice_period=1):
        # python list append operation should be thread safe
        self.objects.append({
            "device_id": device_id,
            "object_id": object_id,
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
                if now - time_last_success_slice > slice_period:
                    data = slicer.execute()
                    object["time_last_success_slice"] = time.time()
                    # collected data can be transmitted to server
                    data[ObjectProperty.DEVICE_ID.id()] = device_id
                    transmitter.push_collected_data(data)
            time.sleep(1)


if __name__ == '__main__':
    visiobas.visiobas_logging.initialize_logging()

    transmitter = VisiobasTransmitter()
    transmitter.setDaemon(True)
    transmitter.start()

    data_collector = VisiobasThreadDataCollector(transmitter)
    data_collector.add_object(device_id=200, object_id=32001, slice_period=5)
    data_collector.add_object(device_id=200, object_id=32002, slice_period=10)
    data_collector.start()
    data_collector.join()
