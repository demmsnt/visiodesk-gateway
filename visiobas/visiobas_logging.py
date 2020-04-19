import logging


def initialize_logging():
    logging.basicConfig(
        format='%(levelname)s %(asctime)-15s %(name)s %(funcName)-8s %(message)s',
        filename='visiobas.log',
        level=logging.DEBUG)
