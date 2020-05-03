import enum

bacnet_name_map = {
    "acked-transitions": "0",
    "ack-required": "1",
    "action": "2",
    "action-text": "3",
    "active-text": "4",
    "active-vt-sessions": "5",
    "alarm-value": "6",
    "alarm-values": "7",
    "all": "8",
    "all-writes-successful": "9",
    "apdu-segment-timeout": "10",
    "apdu-timeout": "11",
    "application-software-version": "12",
    "archive": "13",
    "bias": "14",
    "change-of-state-count": "15",
    "change-of-state-time": "16",
    "notification-class": "17",
    "controlled-variable-reference": "19",
    "controlled-variable-units": "20",
    "controlled-variable-value": "21",
    "cov-increment": "22",
    "date-list": "23",
    "daylight-savings-status": "24",
    "deadband": "25",
    "derivative-constant": "26",
    "derivative-constant-units": "27",
    "description": "28",
    "description-of-halt": "29",
    "device-address-binding": "30",
    "device-type": "31",
    "effective-period": "32",
    "elapsed-active-time": "33",
    "error-limit": "34",
    "event-enable": "35",
    "event-state": "36",
    "event-type": "37",
    "exception-schedule": "38",
    "fault-values": "39",
    "feedback-value": "40",
    "file-access-method": "41",
    "file-size": "42",
    "file-type": "43",
    "firmware-revision": "44",
    "high-limit": "45",
    "inactive-text": "46",
    "in-process": "47",
    "instance-of": "48",
    "integral-constant": "49",
    "integral-constant-units": "50",
    "limit-enable": "52",
    "list-of-group-members": "53",
    "list-of-object-property-references": "54",
    "local-date": "56",
    "local-time": "57",
    "location": "58",
    "low-limit": "59",
    "manipulated-variable-reference": "60",
    "maximum-output": "61",
    "max-apdu-length-accepted": "62",
    "max-info-frames": "63",
    "max-master": "64",
    "max-pres-value": "65",
    "minimum-off-time": "66",
    "minimum-on-time": "67",
    "minimum-output": "68",
    "min-pres-value": "69",
    "model-name": "70",
    "modification-date": "71",
    "notify-type": "72",
    "number-of-apdu-retries": "73",
    "number-of-states": "74",
    "object identifier": "75",
    "object-identifier": "75",
    "object-list": "76",
    "object-name": "77",
    "object-property-reference": "77",
    "object type": "79",
    "object-type": "79",
    "optional": "80",
    "out-of-service": "81",
    "output-units": "82",
    "event-parameters": "83",
    "polarity": "84",
    "present value": "85",
    "present-value": "85",
    "priority": "86",
    "priority-array": "87",
    "priority-for-writing": "88",
    "process-identifier": "89",
    "program-change": "90",
    "program-location": "91",
    "program-state": "92",
    "proportional-constant": "93",
    "proportional-constant-units": "94",
    "protocol-object-types-supported": "96",
    "protocol-services-supported": "97",
    "protocol-version": "98",
    "read-only": "99",
    "reason-for-halt": "100",
    "recipient-list": "102",
    "reliability": "103",
    "relinquish-default": "104",
    "required": "105",
    "resolution": "106",
    "segmentation-supported": "107",
    "setpoint": "108",
    "setpoint-reference": "109",
    "state-text": "110",
    "status-flags": "111",
    "system-status": "112",
    "time-delay": "113",
    "time-of-active-time-reset": "114",
    "time-of-state-count-reset": "115",
    "time-synchronization-recipients": "116",
    "units": "117",
    "update-interval": "118",
    "utc-offset": "119",
    "vendor-identifier": "120",
    "vendor-name": "121",
    "vt-classes-supported": "122",
    "weekly-schedule": "123",
    "attempted-samples": "124",
    "average-value": "125",
    "buffer-size": "126",
    "client-cov-increment": "127",
    "cov-resubscription-interval": "128",
    "event-time-stamps": "130",
    "log-buffer": "131",
    "log-device-object-property": "132",
    "enable": "133",
    "log-interval": "134",
    "maximum-value": "135",
    "minimum-value": "136",
    "notification-threshold": "137",
    "protocol-revision": "139",
    "records-since-notification": "140",
    "record-count": "141",
    "start-time": "142",
    "stop-time": "143",
    "stop-when-full": "144",
    "total-record-count": "145",
    "valid-samples": "146",
    "window-interval": "147",
    "window-samples": "148",
    "maximum-value-timestamp": "149",
    "minimum-value-timestamp": "150",
    "variance-value": "151",
    "active-cov-subscriptions": "152",
    "backup-failure-timeout": "153",
    "configuration-files": "154",
    "database-revision": "155",
    "direct-reading": "156",
    "last-restore-time": "157",
    "maintenance-required": "158",
    "member-of": "159",
    "mode": "160",
    "operation-expected": "161",
    "setting": "162",
    "silenced": "163",
    "tracking-value": "164",
    "zone-members": "165",
    "life-safety-alarm-values": "166",
    "max-segments-accepted": "167",
    "profile-name": "168",
    "auto-slave-discovery": "169",
    "manual-slave-address-binding": "170",
    "slave-address-binding": "171",
    "slave-proxy-enable": "172",
    "last-notify-record": "173",
    "schedule-default": "174",
    "accepted-modes": "175",
    "adjust-value": "176",
    "count": "177",
    "count-before-change": "178",
    "count-change-time": "179",
    "cov-period": "180",
    "input-reference": "181",
    "limit-monitoring-interval": "182",
    "logging-object": "183",
    "logging-record": "184",
    "prescale": "185",
    "pulse-rate": "186",
    "scale": "187",
    "scale-factor": "188",
    "update-time": "189",
    "value-before-change": "190",
    "value-set": "191",
    "value-change-time": "192",
    "align-intervals": "193",
    "interval-offset": "195",
    "last-restart-reason": "196",
    "logging-type": "197",
    "restart-notification-recipients": "202",
    "time-of-device-restart": "203",
    "time-synchronization-interval": "204",
    "trigger": "205",
    "utc-time-synchronization-recipients": "206",
    "node-subtype": "207",
    "node-type": "208",
    "structured-object-list": "209",
    "subordinate-annotations": "210",
    "subordinate-list": "211",
    "actual-shed-level": "212",
    "duty-window": "213",
    "expected-shed-level": "214",
    "full-duty-baseline": "215",
    "requested-shed-level": "218",
    "shed-duration": "219",
    "shed-level-descriptions": "220",
    "shed-levels": "221",
    "state-description": "222",
    "door-alarm-state": "226",
    "door-extended-pulse-time": "227",
    "door-members": "228",
    "door-open-too-long-time": "229",
    "door-pulse-time": "230",
    "door-status": "231",
    "door-unlock-delay-time": "232",
    "lock-status": "233",
    "masked-alarm-values": "234",
    "secured-status": "235",
    "absentee-limit": "244",
    "access-alarm-events": "245",
    "access-doors": "246",
    "access-event": "247",
    "access-event-authentication-factor": "248",
    "access-event-credential": "249",
    "access-event-time": "250",
    "access-transaction-events": "251",
    "accompaniment": "252",
    "accompaniment-time": "253",
    "activation-time": "254",
    "active-authentication-policy": "255",
    "assigned-access-rights": "256",
    "authentication-factors": "257",
    "authentication-policy-list": "258",
    "authentication-policy-names": "259",
    "authentication-status": "260",
    "authorization-mode": "261",
    "belongs-to": "262",
    "credential-disable": "263",
    "credential-status": "264",
    "credentials": "265",
    "credentials-in-zone": "266",
    "days-remaining": "267",
    "entry-points": "268",
    "exit-points": "269",
    "expiry-time": "270",
    "extended-time-enable": "271",
    "failed-attempt-events": "272",
    "failed-attempts": "273",
    "failed-attempts-time": "274",
    "last-access-event": "275",
    "last-access-point": "276",
    "last-credential-added": "277",
    "last-credential-added-time": "278",
    "last-credential-removed": "279",
    "last-credential-removed-time": "280",
    "last-use-time": "281",
    "lockout": "282",
    "lockout-relinquish-time": "283",
    "max-failed-attempts": "285",
    "members": "286",
    "muster-point": "287",
    "negative-access-rules": "288",
    "number-of-authentication-policies": "289",
    "occupancy-count": "290",
    "occupancy-count-adjust": "291",
    "occupancy-count-enable": "292",
    "occupancy-lower-limit": "294",
    "occupancy-lower-limit-enforced": "295",
    "occupancy-state": "296",
    "occupancy-upper-limit": "297",
    "occupancy-upper-limit-enforced": "298",
    "passback-mode": "300",
    "passback-timeout": "301",
    "positive-access-rules": "302",
    "reason-for-disable": "303",
    "supported-formats": "304",
    "supported-format-classes": "305",
    "threat-authority": "306",
    "threat-level": "307",
    "trace-flag": "308",
    "transaction-notification-class": "309",
    "user-external-identifier": "310",
    "user-information-reference": "311",
    "user-name": "317",
    "user-type": "318",
    "uses-remaining": "319",
    "zone-from": "320",
    "zone-to": "321",
    "access-event-tag": "322",
    "global-identifier": "323",
    "verification-time": "326",
    "base-device-security-policy": "327",
    "distribution-key-revision": "328",
    "do-not-hide": "329",
    "key-sets": "330",
    "last-key-server": "331",
    "network-access-security-policies": "332",
    "packet-reorder-time": "333",
    "security-pdu-timeout": "334",
    "security-time-window": "335",
    "supported-security-algorithms": "336",
    "update-key-set-timeout": "337",
    "backup-and-restore-state": "338",
    "backup-preparation-time": "339",
    "restore-completion-time": "340",
    "restore-preparation-time": "341",
    "bit-mask": "342",
    "bit-text": "343",
    "is-utc": "344",
    "group-members": "345",
    "group-member-names": "346",
    "member-status-flags": "347",
    "requested-update-interval": "348",
    "covu-period": "349",
    "covu-recipients": "350",
    "event-message-texts": "351",
    "event-message-texts-config": "352",
    "event-detection-enable": "353",
    "event-algorithm-inhibit": "354",
    "event-algorithm-inhibit-ref": "355",
    "time-delay-normal": "356",
    "reliability-evaluation-inhibit": "357",
    "fault-parameters": "358",
    "fault-type": "359",
    "local-forwarding-only": "360",
    "process-identifier-filter": "361",
    "subscribed-recipients": "362",
    "port-filter": "363",
    "authorization-exemptions": "364",
    "allow-group-delay-inhibit": "365",
    "channel-number": "366",
    "control-groups": "367",
    "execution-delay": "368",
    "last-priority": "369",
    "write-status": "370",
    "property-list": "371",
    "serial-number": "372",
    "blink-warn-enable": "373",
    "default-fade-time": "374",
    "default-ramp-rate": "375",
    "default-step-increment": "376",
    "egress-time": "377",
    "in-progress": "378",
    "instantaneous-power": "379",
    "lighting-command": "380",
    "lighting-command-default-priority": "381",
    "max-actual-value": "382",
    "min-actual-value": "383",
    "power": "384",
    "transition": "385",
    "egress-active": "386"
}


class ObjectProperty(enum.Enum):
    ACKED_TRANSITIONS = '0'
    ACK_REQUIRED = '1'
    ACTION = '2'
    ACTION_TEXT = '3'
    ACTIVE_TEXT = '4'
    ACTIVE_VT_SESSIONS = '5'
    ALARM_VALUE = '6'
    ALARM_VALUES = '7'
    ALL = '8'
    ALL_WRITES_SUCCESSFUL = '9'
    APDU_SEGMENT_TIMEOUT = '10'
    APDU_TIMEOUT = '11'
    APPLICATION_SOFTWARE_VERSION = '12'
    ARCHIVE = '13'
    BIAS = '14'
    CHANGE_OF_STATE_COUNT = '15'
    CHANGE_OF_STATE_TIME = '16'
    NOTIFICATION_CLASS = '17'
    CONTROLLED_VARIABLE_REFERENCE = '19'
    CONTROLLED_VARIABLE_UNITS = '20'
    CONTROLLED_VARIABLE_VALUE = '21'
    COV_INCREMENT = '22'
    DATE_LIST = '23'
    DAYLIGHT_SAVINGS_STATUS = '24'
    DEADBAND = '25'
    DERIVATIVE_CONSTANT = '26'
    DERIVATIVE_CONSTANT_UNITS = '27'
    DESCRIPTION = '28'
    DESCRIPTION_OF_HALT = '29'
    DEVICE_ADDRESS_BINDING = '30'
    DEVICE_TYPE = '31'
    EFFECTIVE_PERIOD = '32'
    ELAPSED_ACTIVE_TIME = '33'
    ERROR_LIMIT = '34'
    EVENT_ENABLE = '35'
    EVENT_STATE = '36'
    EVENT_TYPE = '37'
    EXCEPTION_SCHEDULE = '38'
    FAULT_VALUES = '39'
    FEEDBACK_VALUE = '40'
    FILE_ACCESS_METHOD = '41'
    FILE_SIZE = '42'
    FILE_TYPE = '43'
    FIRMWARE_REVISION = '44'
    HIGH_LIMIT = '45'
    INACTIVE_TEXT = '46'
    IN_PROCESS = '47'
    INSTANCE_OF = '48'
    INTEGRAL_CONSTANT = '49'
    INTEGRAL_CONSTANT_UNITS = '50'
    LIMIT_ENABLE = '52'
    LIST_OF_GROUP_MEMBERS = '53'
    LIST_OF_OBJECT_PROPERTY_REFERENCES = '54'
    LOCAL_DATE = '56'
    LOCAL_TIME = '57'
    LOCATION = '58'
    LOW_LIMIT = '59'
    MANIPULATED_VARIABLE_REFERENCE = '60'
    MAXIMUM_OUTPUT = '61'
    MAX_APDU_LENGTH_ACCEPTED = '62'
    MAX_INFO_FRAMES = '63'
    MAX_MASTER = '64'
    MAX_PRES_VALUE = '65'
    MINIMUM_OFF_TIME = '66'
    MINIMUM_ON_TIME = '67'
    MINIMUM_OUTPUT = '68'
    MIN_PRES_VALUE = '69'
    MODEL_NAME = '70'
    MODIFICATION_DATE = '71'
    NOTIFY_TYPE = '72'
    NUMBER_OF_APDU_RETRIES = '73'
    NUMBER_OF_STATES = '74'
    OBJECT_IDENTIFIER = '75'
    OBJECT_LIST = '76'
    OBJECT_PROPERTY_REFERENCE = '77'
    OBJECT_TYPE = '79'
    OPTIONAL = '80'
    OUT_OF_SERVICE = '81'
    OUTPUT_UNITS = '82'
    EVENT_PARAMETERS = '83'
    POLARITY = '84'
    PRESENT_VALUE = '85'
    PRIORITY = '86'
    PRIORITY_ARRAY = '87'
    PRIORITY_FOR_WRITING = '88'
    PROCESS_IDENTIFIER = '89'
    PROGRAM_CHANGE = '90'
    PROGRAM_LOCATION = '91'
    PROGRAM_STATE = '92'
    PROPORTIONAL_CONSTANT = '93'
    PROPORTIONAL_CONSTANT_UNITS = '94'
    PROTOCOL_OBJECT_TYPES_SUPPORTED = '96'
    PROTOCOL_SERVICES_SUPPORTED = '97'
    PROTOCOL_VERSION = '98'
    READ_ONLY = '99'
    REASON_FOR_HALT = '100'
    RECIPIENT_LIST = '102'
    RELIABILITY = '103'
    RELINQUISH_DEFAULT = '104'
    REQUIRED = '105'
    RESOLUTION = '106'
    SEGMENTATION_SUPPORTED = '107'
    SETPOINT = '108'
    SETPOINT_REFERENCE = '109'
    STATE_TEXT = '110'
    STATUS_FLAGS = '111'
    SYSTEM_STATUS = '112'
    TIME_DELAY = '113'
    TIME_OF_ACTIVE_TIME_RESET = '114'
    TIME_OF_STATE_COUNT_RESET = '115'
    TIME_SYNCHRONIZATION_RECIPIENTS = '116'
    UNITS = '117'
    UPDATE_INTERVAL = '118'
    UTC_OFFSET = '119'
    VENDOR_IDENTIFIER = '120'
    VENDOR_NAME = '121'
    VT_CLASSES_SUPPORTED = '122'
    WEEKLY_SCHEDULE = '123'
    ATTEMPTED_SAMPLES = '124'
    AVERAGE_VALUE = '125'
    BUFFER_SIZE = '126'
    CLIENT_COV_INCREMENT = '127'
    COV_RESUBSCRIPTION_INTERVAL = '128'
    EVENT_TIME_STAMPS = '130'
    LOG_BUFFER = '131'
    LOG_DEVICE_OBJECT_PROPERTY = '132'
    ENABLE = '133'
    LOG_INTERVAL = '134'
    MAXIMUM_VALUE = '135'
    MINIMUM_VALUE = '136'
    NOTIFICATION_THRESHOLD = '137'
    PROTOCOL_REVISION = '139'
    RECORDS_SINCE_NOTIFICATION = '140'
    RECORD_COUNT = '141'
    START_TIME = '142'
    STOP_TIME = '143'
    STOP_WHEN_FULL = '144'
    TOTAL_RECORD_COUNT = '145'
    VALID_SAMPLES = '146'
    WINDOW_INTERVAL = '147'
    WINDOW_SAMPLES = '148'
    MAXIMUM_VALUE_TIMESTAMP = '149'
    MINIMUM_VALUE_TIMESTAMP = '150'
    VARIANCE_VALUE = '151'
    ACTIVE_COV_SUBSCRIPTIONS = '152'
    BACKUP_FAILURE_TIMEOUT = '153'
    CONFIGURATION_FILES = '154'
    DATABASE_REVISION = '155'
    DIRECT_READING = '156'
    LAST_RESTORE_TIME = '157'
    MAINTENANCE_REQUIRED = '158'
    MEMBER_OF = '159'
    MODE = '160'
    OPERATION_EXPECTED = '161'
    SETTING = '162'
    SILENCED = '163'
    TRACKING_VALUE = '164'
    ZONE_MEMBERS = '165'
    LIFE_SAFETY_ALARM_VALUES = '166'
    MAX_SEGMENTS_ACCEPTED = '167'
    PROFILE_NAME = '168'
    AUTO_SLAVE_DISCOVERY = '169'
    MANUAL_SLAVE_ADDRESS_BINDING = '170'
    SLAVE_ADDRESS_BINDING = '171'
    SLAVE_PROXY_ENABLE = '172'
    LAST_NOTIFY_RECORD = '173'
    SCHEDULE_DEFAULT = '174'
    ACCEPTED_MODES = '175'
    ADJUST_VALUE = '176'
    COUNT = '177'
    COUNT_BEFORE_CHANGE = '178'
    COUNT_CHANGE_TIME = '179'
    COV_PERIOD = '180'
    INPUT_REFERENCE = '181'
    LIMIT_MONITORING_INTERVAL = '182'
    LOGGING_OBJECT = '183'
    LOGGING_RECORD = '184'
    PRESCALE = '185'
    PULSE_RATE = '186'
    SCALE = '187'
    SCALE_FACTOR = '188'
    UPDATE_TIME = '189'
    VALUE_BEFORE_CHANGE = '190'
    VALUE_SET = '191'
    VALUE_CHANGE_TIME = '192'
    ALIGN_INTERVALS = '193'
    INTERVAL_OFFSET = '195'
    LAST_RESTART_REASON = '196'
    LOGGING_TYPE = '197'
    RESTART_NOTIFICATION_RECIPIENTS = '202'
    TIME_OF_DEVICE_RESTART = '203'
    TIME_SYNCHRONIZATION_INTERVAL = '204'
    TRIGGER = '205'
    UTC_TIME_SYNCHRONIZATION_RECIPIENTS = '206'
    NODE_SUBTYPE = '207'
    NODE_TYPE = '208'
    STRUCTURED_OBJECT_LIST = '209'
    SUBORDINATE_ANNOTATIONS = '210'
    SUBORDINATE_LIST = '211'
    ACTUAL_SHED_LEVEL = '212'
    DUTY_WINDOW = '213'
    EXPECTED_SHED_LEVEL = '214'
    FULL_DUTY_BASELINE = '215'
    REQUESTED_SHED_LEVEL = '218'
    SHED_DURATION = '219'
    SHED_LEVEL_DESCRIPTIONS = '220'
    SHED_LEVELS = '221'
    STATE_DESCRIPTION = '222'
    DOOR_ALARM_STATE = '226'
    DOOR_EXTENDED_PULSE_TIME = '227'
    DOOR_MEMBERS = '228'
    DOOR_OPEN_TOO_LONG_TIME = '229'
    DOOR_PULSE_TIME = '230'
    DOOR_STATUS = '231'
    DOOR_UNLOCK_DELAY_TIME = '232'
    LOCK_STATUS = '233'
    MASKED_ALARM_VALUES = '234'
    SECURED_STATUS = '235'
    ABSENTEE_LIMIT = '244'
    ACCESS_ALARM_EVENTS = '245'
    ACCESS_DOORS = '246'
    ACCESS_EVENT = '247'
    ACCESS_EVENT_AUTHENTICATION_FACTOR = '248'
    ACCESS_EVENT_CREDENTIAL = '249'
    ACCESS_EVENT_TIME = '250'
    ACCESS_TRANSACTION_EVENTS = '251'
    ACCOMPANIMENT = '252'
    ACCOMPANIMENT_TIME = '253'
    ACTIVATION_TIME = '254'
    ACTIVE_AUTHENTICATION_POLICY = '255'
    ASSIGNED_ACCESS_RIGHTS = '256'
    AUTHENTICATION_FACTORS = '257'
    AUTHENTICATION_POLICY_LIST = '258'
    AUTHENTICATION_POLICY_NAMES = '259'
    AUTHENTICATION_STATUS = '260'
    AUTHORIZATION_MODE = '261'
    BELONGS_TO = '262'
    CREDENTIAL_DISABLE = '263'
    CREDENTIAL_STATUS = '264'
    CREDENTIALS = '265'
    CREDENTIALS_IN_ZONE = '266'
    DAYS_REMAINING = '267'
    ENTRY_POINTS = '268'
    EXIT_POINTS = '269'
    EXPIRY_TIME = '270'
    EXTENDED_TIME_ENABLE = '271'
    FAILED_ATTEMPT_EVENTS = '272'
    FAILED_ATTEMPTS = '273'
    FAILED_ATTEMPTS_TIME = '274'
    LAST_ACCESS_EVENT = '275'
    LAST_ACCESS_POINT = '276'
    LAST_CREDENTIAL_ADDED = '277'
    LAST_CREDENTIAL_ADDED_TIME = '278'
    LAST_CREDENTIAL_REMOVED = '279'
    LAST_CREDENTIAL_REMOVED_TIME = '280'
    LAST_USE_TIME = '281'
    LOCKOUT = '282'
    LOCKOUT_RELINQUISH_TIME = '283'
    MAX_FAILED_ATTEMPTS = '285'
    MEMBERS = '286'
    MUSTER_POINT = '287'
    NEGATIVE_ACCESS_RULES = '288'
    NUMBER_OF_AUTHENTICATION_POLICIES = '289'
    OCCUPANCY_COUNT = '290'
    OCCUPANCY_COUNT_ADJUST = '291'
    OCCUPANCY_COUNT_ENABLE = '292'
    OCCUPANCY_LOWER_LIMIT = '294'
    OCCUPANCY_LOWER_LIMIT_ENFORCED = '295'
    OCCUPANCY_STATE = '296'
    OCCUPANCY_UPPER_LIMIT = '297'
    OCCUPANCY_UPPER_LIMIT_ENFORCED = '298'
    PASSBACK_MODE = '300'
    PASSBACK_TIMEOUT = '301'
    POSITIVE_ACCESS_RULES = '302'
    REASON_FOR_DISABLE = '303'
    SUPPORTED_FORMATS = '304'
    SUPPORTED_FORMAT_CLASSES = '305'
    THREAT_AUTHORITY = '306'
    THREAT_LEVEL = '307'
    TRACE_FLAG = '308'
    TRANSACTION_NOTIFICATION_CLASS = '309'
    USER_EXTERNAL_IDENTIFIER = '310'
    USER_INFORMATION_REFERENCE = '311'
    USER_NAME = '317'
    USER_TYPE = '318'
    USES_REMAINING = '319'
    ZONE_FROM = '320'
    ZONE_TO = '321'
    ACCESS_EVENT_TAG = '322'
    GLOBAL_IDENTIFIER = '323'
    VERIFICATION_TIME = '326'
    BASE_DEVICE_SECURITY_POLICY = '327'
    DISTRIBUTION_KEY_REVISION = '328'
    DO_NOT_HIDE = '329'
    KEY_SETS = '330'
    LAST_KEY_SERVER = '331'
    NETWORK_ACCESS_SECURITY_POLICIES = '332'
    PACKET_REORDER_TIME = '333'
    SECURITY_PDU_TIMEOUT = '334'
    SECURITY_TIME_WINDOW = '335'
    SUPPORTED_SECURITY_ALGORITHMS = '336'
    UPDATE_KEY_SET_TIMEOUT = '337'
    BACKUP_AND_RESTORE_STATE = '338'
    BACKUP_PREPARATION_TIME = '339'
    RESTORE_COMPLETION_TIME = '340'
    RESTORE_PREPARATION_TIME = '341'
    BIT_MASK = '342'
    BIT_TEXT = '343'
    IS_UTC = '344'
    GROUP_MEMBERS = '345'
    GROUP_MEMBER_NAMES = '346'
    MEMBER_STATUS_FLAGS = '347'
    REQUESTED_UPDATE_INTERVAL = '348'
    COVU_PERIOD = '349'
    COVU_RECIPIENTS = '350'
    EVENT_MESSAGE_TEXTS = '351'
    EVENT_MESSAGE_TEXTS_CONFIG = '352'
    EVENT_DETECTION_ENABLE = '353'
    EVENT_ALGORITHM_INHIBIT = '354'
    EVENT_ALGORITHM_INHIBIT_REF = '355'
    TIME_DELAY_NORMAL = '356'
    RELIABILITY_EVALUATION_INHIBIT = '357'
    FAULT_PARAMETERS = '358'
    FAULT_TYPE = '359'
    LOCAL_FORWARDING_ONLY = '360'
    PROCESS_IDENTIFIER_FILTER = '361'
    SUBSCRIBED_RECIPIENTS = '362'
    PORT_FILTER = '363'
    AUTHORIZATION_EXEMPTIONS = '364'
    ALLOW_GROUP_DELAY_INHIBIT = '365'
    CHANNEL_NUMBER = '366'
    CONTROL_GROUPS = '367'
    EXECUTION_DELAY = '368'
    LAST_PRIORITY = '369'
    WRITE_STATUS = '370'
    PROPERTY_LIST = '371'
    SERIAL_NUMBER = '372'
    BLINK_WARN_ENABLE = '373'
    DEFAULT_FADE_TIME = '374'
    DEFAULT_RAMP_RATE = '375'
    DEFAULT_STEP_INCREMENT = '376'
    EGRESS_TIME = '377'
    IN_PROGRESS = '378'
    INSTANTANEOUS_POWER = '379'
    LIGHTING_COMMAND = '380'
    LIGHTING_COMMAND_DEFAULT_PRIORITY = '381'
    MAX_ACTUAL_VALUE = '382'
    MIN_ACTUAL_VALUE = '383'
    POWER = '384'
    TRANSITION = '385'
    EGRESS_ACTIVE = '386'
    DEVICE_ID = '846'

    def id(self):
        return self.value


class ObjectType(enum.Enum):
    ANALOG_INPUT = "analog-input", 0
    ANALOG_OUTPUT = "analog-output", 1
    ANALOG_VALUE = "analog-value", 2
    BINARY_INPUT = "binary-input", 3
    BINARY_OUTPUT = "binary-output", 4
    BINARY_VALUE = "binary-value", 5
    DEVICE = "device", 8
    CALENDAR = "calendar", 6
    COMMAND = "command", 7
    EVENT_ENROLLMENT = "event-enrollment", 9
    FILE = "file", 10
    GROUP = "group", 11
    LOOP = "loop", 12
    MULTI_STATE_INPUT = "multi-state-input", 13
    NOTIFICATION_CLASS = "notification-class", 15
    MULTI_STATE_OUTPUT = "multi-state-output", 14
    PROGRAM = "program", 16
    SCHEDULE = "schedule", 17
    AVERAGING = "averaging", 18
    MULTI_STATE_VALUE = "multi-state-value", 19
    ACCUMULATOR = "accumulator", 23
    TREND_LOG = "trend-log", 20
    LIFE_SAFETY_POINT = "life-safety-point", 21
    LIFE_SAFETY_ZONE = "life-safety-zone", 22
    PULSE_CONVERTER = "pulse-converter", 24
    ACCESS_POINT = "access-point", 33
    SITE = "site", -1
    FOLDER = "folder", -1
    TRUNK = "trunk", -1
    GRAPHIC = "graphic", -1

    def id(self):
        return self.value[0]

    def name(self):
        return self.value[0]

    def code(self):
        return self.value[1]

    @staticmethod
    def name_to_code(name):
        for _type in ObjectType:
            if _type.name() == name:
                return _type.code()
        return None
