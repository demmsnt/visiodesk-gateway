import enum


class ItemType(enum):
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


class TopicType(enum):
    EVENT = 1
    REQUEST = 2
    TASK = 3
    OFFER = 4

    def id(self):
        return self.value


class TopicStatus(enum):
    NEW = 1
    ASSIGNED = 2
    IN_PROGRESS = 3
    ON_HOLD = 4
    RESOLVED = 5
    CLOSED = 6

    def id(self):
        return self.value


class TopicPriority(enum):
    LOW = 1,
    NORM = 2
    HEED = 3
    TOP = 4

    def id(self):
        return self.value
