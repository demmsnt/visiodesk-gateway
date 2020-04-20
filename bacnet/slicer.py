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

    def execute(self, device_id, object_type_code, object_id, fields):
        path = Path(self.bacrpm_app_path)
        cwd = path.parent
        command = " ".join([
            self.bacrpm_app_path,
            str(device_id),
            str(object_type_code),
            str(object_id),
            ",".join(fields)
        ])
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("execute: {} cwd: {}".format(command, cwd))
        process = Popen(command, stdout=PIPE, cwd=str(cwd), text=True)
        (output, err) = process.communicate()
        exit_code = process.wait()
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("bacrpm output:\n{}".format(output))
            self.logger.debug("exit code: {}".format(exit_code))
        try:
            return self.parser.parse_bacrpm(output)
        except Exception as e:
            self.logger.error("Failed parse bacrpm: {}".format(e))
            self.logger.error("Failed parser: {}".format(output))
