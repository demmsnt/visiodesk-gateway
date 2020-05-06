import argparse
import logging
import traceback

from visiobas.visiobas_logging import initialize_logging
from visiobas.gate_client import VisiobasGateClient
import bacnet.config
from bacnet.bacnet import ObjectProperty
from bacnet.writer import BACnetWriter
from visiobas.object.device import Device


def print_help():
    print("usage create_address_cache.py:")
    print("create_address_cache.py --devices <list of devices>")
    print("example of request from server devices 200,300 and 400 and create address_cache file")
    print("python create_address_cache.py --devices 200,300,400")


if __name__ == "__main__":
    initialize_logging()
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser()
    parser.add_argument('--devices', type=str, default="")
    args = parser.parse_args()
    if args.devices == "":
        logger.error("--devices request list of devices separated by comma ','")
        print_help()
        exit(0)
    devices = [int(x) for x in args.devices.split(",")]
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("create address cache for devices: {}".format(devices))

    server = bacnet.config.visiobas_server
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("using visiobas server {}:{}".format(server['host'], server['port']))

    client = VisiobasGateClient(server['host'], server['port'], server['ssl_verify'])
    client.rq_login(server['auth']['user'], server['auth']['pwd'])
    try:
        server_devices = client.rq_devices()
        server_devices = filter(lambda o: o[ObjectProperty.OBJECT_IDENTIFIER.id()] in devices, server_devices)
        bacwi_devices = []
        for o in server_devices:
            device = Device(o)
            bacwi_devices.append({
                'id': device.get_id(),
                'host': device.get_host(),
                'port': device.get_port(),
                'apdu': device.get_apdu()
            })
        BACnetWriter.write_bacwi(bacwi_devices, 'address_cache')
        client.rq_logout()
    except BaseException as e:
        client.rq_logout()
        logger.error("Failed create bacwi table: {}".format(e))
        logger.error(traceback.format_exc())
        raise e
