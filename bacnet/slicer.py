from subprocess import Popen, PIPE
from bacnet.parser import BACnetParser
import logging
from pathlib import Path


class BACrpmSlicer:
    def __init__(self, bacrpm_app_path):
        """
        :param bacrpm_app_path:
        """
        self.bacrpm_app_path = bacrpm_app_path
        self.parser = BACnetParser()
        self.logger = logging.getLogger(__name__)

    def execute(self):
        path = Path(self.bacrpm_app_path)
        cwd = path.parent
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("execute: {} cwd: {}".format(self.bacrpm_app_path, cwd))
        process = Popen([self.bacrpm_app_path], stdout=PIPE, cwd=str(cwd), text=True)
        (output, err) = process.communicate()
        exit_code = process.wait()
        # output = str(output)
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("bacrpm output:\n{}".format(output))
            self.logger.debug("exit code: {}".format(exit_code))

        try:
            return self.parser.parse_bacrpm(output)
        except Exception as e:
            self.logger.error("Failed parse bacrpm: {}".format(e))
            self.logger.error("Failed parser: {}".format(output))
