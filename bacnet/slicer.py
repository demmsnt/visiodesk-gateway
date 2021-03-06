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
        self.execute_bacrp_on_fail_bacrpm = True

    def __execute_app(self, args, cwd, timeout):
        cp = subprocess.run(args, stdout=PIPE, stderr=PIPE, cwd=str(cwd), timeout=timeout)
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
                                     fields=kwargs.get("fields"),
                                     timeout=kwargs.get("timeout"))
        elif read_app == "bacrpm":
            data = self.execute_bacrpm(device_id=kwargs.get("device_id"),
                                       object_type=kwargs.get("object_type"),
                                       object_id=kwargs.get("object_id"),
                                       fields=kwargs.get("fields"),
                                       timeout=kwargs.get("timeout"))
            if len(data) == 0 and self.execute_bacrp_on_fail_bacrpm:
                data = self.execute_barp(device_id=kwargs.get("device_id"),
                                         object_type=kwargs.get("object_type"),
                                         object_id=kwargs.get("object_id"),
                                         fields=kwargs.get("fields"),
                                         timeout=kwargs.get("timeout"))
            return data
        else:
            raise Exception("Unsupported read app: {}".format(read_app))

    def execute_barp(self, device_id: int, object_type, object_id: int, fields: list, timeout: int):
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
            output = self.__execute_app(args, path.parent, timeout)
            if output is not None and not len(output) == 0:
                try:
                    self.parser.parse_bacrp(output, field, data)
                except:
                    self.logger.error("bacrpm {}".format(" ".join(args)))
                    self.logger.exception("Failed parse bacrp output:\n{}".format(output))
        return data

    def execute_bacrpm(self, device_id: int, object_type, object_id: int, fields: list, timeout):
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
        output = self.__execute_app(args, cwd, timeout)
        try:
            return self.parser.parse_bacrpm(output)
        except Exception as e:
            self.logger.error("bacrpm {}".format(" ".join(args)))
            self.logger.exception("Failed parse bacrpm, output:\n{}".format(output))
