import logging
import subprocess
from subprocess import PIPE

from bacnet.parser import BACnetParser
from bacnet.bacnet import ObjectType


class BACnetSlicer:
    def __init__(self, config: dict):
        """
        :param bacrpm_app_path:
        """
        self.config = config
        self.parser = BACnetParser()
        self.logger = logging.getLogger('bacnet.slicer')
        self.execute_bacrp_on_fail_bacrpm = False

    def __execute_app(self, args, cwd):
        cp = subprocess.run(args, stdout=PIPE, stderr=PIPE, cwd=str(cwd))
        output = cp.stdout.decode('ascii')
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("execute: {} cwd: {}".format(" ".join(args), cwd))
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("bacrp output: {}".format(output))
        return output

    def execute(self, read_app: str, **kwargs):
        if read_app == "bacrp":
            return self.execute_barp(device_id=kwargs.get("device_id"),
                                     object_type=kwargs.get("object_type"),
                                     object_id=kwargs.get("object_id"),
                                     fields=kwargs.get("fields"))
        elif read_app == "bacrpm":
            data = self.execute_bacrpm(device_id=kwargs.get("device_id"),
                                       object_type=kwargs.get("object_type"),
                                       object_id=kwargs.get("object_id"),
                                       fields=kwargs.get("fields"))
            if len(data) == 0 and self.execute_bacrp_on_fail_bacrpm:
                data = self.execute_barp(device_id=kwargs.get("device_id"),
                                         object_type=kwargs.get("object_type"),
                                         object_id=kwargs.get("object_id"),
                                         fields=kwargs.get("fields"))
            return data
        else:
            raise Exception("Unsupported read app: {}".format(read_app))

    def execute_barp(self, device_id: int, object_type, object_id: int, fields: list):
        if type(object_type) == ObjectType:
            object_type = object_type.code()
        assert (type(object_type) == int)

        path = self.config["bacrp"]
        data = {}
        for field in fields:
            args = [
                str(path),
                str(device_id),
                str(object_type),
                str(object_id),
                str(field)
            ]
            output = self.__execute_app(args, path.parent)
            try:
                self.parser.parse_bacrp(output, field, data)
            except Exception as e:
                self.logger.error("Failed parse bacrpm: {}".format(e))
                self.logger.error("Failed parser: {}".format(output))
        return data

    def execute_bacrpm(self, device_id: int, object_type, object_id: int, fields: list):
        if type(object_type) == ObjectType:
            object_type = object_type.code()
        assert (type(object_type) == int)
        path = self.config["bacrpm"]
        cwd = path.parent
        args = [
            str(path),
            str(device_id),
            str(object_type),
            str(object_id),
            ",".join(fields)
        ]
        output = self.__execute_app(args, cwd)
        try:
            output = "BACnet Reject: Unrecognized Service"
            return self.parser.parse_bacrpm(output)
        except Exception as e:
            self.logger.error("Failed parse bacrpm: {}".format(e))
            self.logger.error("Failed parser: {}".format(output))
