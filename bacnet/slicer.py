from subprocess import Popen, PIPE
from bacnet.parser import BACnetParser
import logging


class BACrpmSlicer:
    def __init__(self, bacrpm_app_path, data_consumer):
        """
        :param bacrpm_app_path:
        :param data_consumer:
        :type data_consumer function - callback function with sliced data
        """
        self.bacrpm_app_path = bacrpm_app_path
        self.data_consumer = data_consumer
        self.parser = BACnetParser()
        self.logger = logging.getLogger(__name__)

    def execute(self):
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("execute {}".format(self.bacrpm_app_path))

        process = Popen([self.bacrpm_app_path], stdout=PIPE)
        (output, err) = process.communicate()
        exit_code = process.wait()

        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("bacrpm output:\n{}".format(output))

        try:
            self.data_consumer(self.parser.parse_bacrpm(output))
        except:
            self.logger.error("Failed parse bacrpm output:\n{}".format(output))
