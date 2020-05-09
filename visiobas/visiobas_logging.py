import logging


def initialize_logging():
    logging.basicConfig(
        format='%(levelname)s %(asctime)-15s %(name)s %(funcName)-8s %(message)s',
        filename='visiobas.log',
        level=logging.INFO)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    loggers = {
        'bacnet.parser': logging.getLogger("bacnet.parser"),
        'bacnet.slicer': logging.getLogger('bacnet.slicer'),
        'visiobas.data_collector': logging.getLogger('visiobas.data_collector'),
        'visiobas.data_collector.notifier': logging.getLogger('visiobas.data_collector.notifier'),
        'visiobas.data_collector.collector': logging.getLogger('visiobas.data_collector.collector'),
        'visiobas.data_collector.transmitter': logging.getLogger('visiobas.data_collector.transmitter')
    }
    loggers['bacnet.parser'].setLevel(logging.INFO)
    loggers['bacnet.slicer'].setLevel(logging.INFO)
    loggers['visiobas.data_collector'].setLevel(logging.INFO)
    loggers['visiobas.data_collector.notifier'].setLevel(logging.INFO)
    loggers['visiobas.data_collector.collector'].setLevel(logging.INFO)
    loggers['visiobas.data_collector.transmitter'].setLevel(logging.INFO)
