from .proto.EventType_pb2 import EventType as EventType_pb2
from enum import Enum


class EventType(Enum):
    """An enumeration describing the different types of events."""

    ALARM = 1
    LOG_FILE = 2
    TEST_SESSION = 3
    CUSTOM = 4

    def to_event_type_pb2(self) -> EventType_pb2:
        return EVENT_TYPE_MAP.get(self.value)

    @staticmethod
    def from_event_type_pb2(event_type: EventType_pb2):
        return EVENT_TYPE_PB2_MAP.get(event_type)


EVENT_TYPE_MAP = {
    1: EventType_pb2.EVENT_TYPE_ALARM,
    2: EventType_pb2.EVENT_TYPE_LOG_FILE,
    3: EventType_pb2.EVENT_TYPE_TEST_SESSION,
    4: EventType_pb2.EVENT_TYPE_CUSTOM
}

EVENT_TYPE_PB2_MAP = {
    EventType_pb2.EVENT_TYPE_ALARM: EventType.ALARM,
    EventType_pb2.EVENT_TYPE_LOG_FILE: EventType.LOG_FILE,
    EventType_pb2.EVENT_TYPE_TEST_SESSION: EventType.TEST_SESSION,
    EventType_pb2.EVENT_TYPE_CUSTOM: EventType.CUSTOM
}
