import logging
from subprocess import Popen, PIPE

from bacnet.parser import BACnetParser


class BACrpmSlicer:
    def __init__(self, config: dict):
        """
        :param bacrpm_app_path:
        """
        self.config = config
        self.parser = BACnetParser()
        self.logger = logging.getLogger('bacnet.slicer')
        self.execute_bacrp_on_fail_bacrpm = False

    def execute(self, read_app: str, **kwargs):
        if read_app == "bacrp":
            self.execute_barp(device_id=kwargs.get("device_id"),
                              object_type_code=kwargs.get("object_type_code"),
                              object_id=kwargs.get("object_id"),
                              fields=kwargs.get("fields"))
        elif read_app == "bacrpm":
            data = self.execute_bacrpm(device_id=kwargs.get("device_id"),
                                       object_type_code=kwargs.get("object_type_code"),
                                       object_id=kwargs.get("object_id"),
                                       fields=kwargs.get("fields"))
            if len(data) == 0 and self.execute_bacrp_on_fail_bacrpm:
                return self.execute_barp(device_id=kwargs.get("device_id"),
                                         object_type_code=kwargs.get("object_type_code"),
                                         object_id=kwargs.get("object_id"),
                                         fields=kwargs.get("fields"))
        else:
            raise Exception("Unsupported slicer read app: {}".format(read_app))

    def execute_barp(self, device_id: int, object_type_code: int, object_id: int, fields: list):
        path = self.config["bacrp"]
        cwd = path.parent
        data = {}
        for field in fields:
            command = " ".join([
                str(path),
                str(device_id),
                str(object_type_code),
                str(object_id),
                str(field)
            ])
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug("execute: {} cwd: {}".format(command, cwd))
            process = Popen(command, stdout=PIPE, cwd=str(cwd), text=True)
            (output, err) = process.communicate()
            exit_code = process.wait()
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug("bacrp output:\n{}".format(output))
                self.logger.debug("exit code: {}".format(exit_code))
            try:
                self.parser.parse_bacrp(output, field, data)
            except Exception as e:
                self.logger.error("Failed parse bacrpm: {}".format(e))
                self.logger.error("Failed parser: {}".format(output))
        return data

    def execute_bacrpm(self, device_id: int, object_type_code: int, object_id: int, fields: list):
        path = self.config["bacrpm"]
        # path = Path(self.bacrpm_app_path)
        cwd = path.parent
        command = " ".join([
            str(path),
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

    # def execute(self, device_id: int, object_type_code: int, object_id: int, fields: list):
    #     path = Path(self.bacrpm_app_path)
    #     cwd = path.parent
    #     command = " ".join([
    #         str(self.bacrpm_app_path),
    #         str(device_id),
    #         str(object_type_code),
    #         str(object_id),
    #         ",".join(fields)
    #     ])
    #     if self.logger.isEnabledFor(logging.DEBUG):
    #         self.logger.debug("execute: {} cwd: {}".format(command, cwd))
    #     process = Popen(command, stdout=PIPE, cwd=str(cwd), text=True)
    #     (output, err) = process.communicate()
    #     exit_code = process.wait()
    #     if self.logger.isEnabledFor(logging.DEBUG):
    #         self.logger.debug("bacrpm output:\n{}".format(output))
    #         self.logger.debug("exit code: {}".format(exit_code))
    #     try:
    #         return self.parser.parse_bacrpm(output)
    #     except Exception as e:
    #         self.logger.error("Failed parse bacrpm: {}".format(e))
    #         self.logger.error("Failed parser: {}".format(output))
