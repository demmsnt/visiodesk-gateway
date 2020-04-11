import enum


class ObjectType(enum.Enum):
    ANALOG_INPUT = "analog-input"
    ANALOG_OUTPUT = "analog-output"
    ANALOG_VALUE = "analog-value"
    BINARY_INPUT = "binary-input"
    BINARY_OUTPUT = "binary-output"
    BINARY_VALUE = "binary-value"
    DEVICE = "device"
    CALENDAR = "calendar"
    COMMAND = "command"
    EVENT_ENROLLMENT = "event-enrollment"
    FILE = "file"
    GROUP = "group"
    LOOP = "loop"
    MULTI_STATE_INPUT = "multi-state-input"
    NOTIFICATION_CLASS = "notification-class"
    MULTI_STATE_OUTPUT = "multi-state-output"
    PROGRAM = "program"
    SCHEDULE = "schedule"
    AVERAGING = "averaging"
    MULTI_STATE_VALUE = "multi-state-value"
    ACCUMULATOR = "accumulator"
    TREND_LOG = "trend-log"
    LIFE_SAFETY_POINT = "life-safety-point"
    LIFE_SAFETY_ZONE = "life-safety-zone"
    PULSE_CONVERTER = "pulse-converter"
    ACCESS_POINT = "access-point"
    SITE = "site"
    FOLDER = "folder"
    TRUNK = "trunk"
    GRAPHIC = "graphic"

    def id(self):
        return self.value
