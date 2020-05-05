import enum


class ItemType(enum.Enum):
    IMAGE = 1
    DOCUMENT = 2
    USER = 3
    GROUP = 4
    PRIORITY = 5
    STATUS = 6
    PROBLEM = 7
    PLANING_ENDING_DATE = 8
    ACTUAL_ENDING_DATE = 9
    AUDIO = 10
    LOCATION = 11
    METING = 12
    MESSAGE = 13
    CHECK = 14
    REMOVED_FROM_GROUP = 15
    REMOVED_FROM_USER = 16

    def id(self):
        return self.value


class TopicType(enum.Enum):
    EVENT = 1
    REQUEST = 2
    TASK = 3
    OFFER = 4

    def id(self):
        return self.value


class TopicStatus(enum.Enum):
    NEW = 1, "new"
    ASSIGNED = 2, "assigned"
    IN_PROGRESS = 3, "in_progress"
    ON_HOLD = 4, "on_hold"
    RESOLVED = 5, "resolved"
    CLOSED = 6, "closed"

    def id(self):
        return self.value[0]

    def name(self):
        return self.value[1]


class TopicPriority(enum.Enum):
    LOW = 1, "low"
    NORM = 2, "norm"
    HEED = 3, "heed"
    TOP = 4, "top"

    def id(self):
        return self.value[0]

    def name(self):
        return self.value[1]
