from enum import Enum
from .proto.StartTriggerCondition_pb2 import StartTriggerCondition as StartTriggerCondition_pb2


class StartTriggerCondition(Enum):
    """An enumeration describing when to the logging starts."""

    """Manually begin logging by clicking RUN."""
    TEST_START = 0

    """Begin logging when the value of the channel meets the specified value change condition."""
    CHANNEL_VALUE_CHANGE = 1

    """Begin logging at a designated date and time."""
    ABSOLUTE_TIME = 2

    def to_start_trigger_condition_pb2(self) -> StartTriggerCondition_pb2:
        return START_TRIGGER_CONDITION_MAP.get(self.value)

    @staticmethod
    def from_start_trigger_condition_pb2(start_trigger_condition: StartTriggerCondition_pb2):
        return START_TRIGGER_CONDITION_PB2_MAP.get(start_trigger_condition)


START_TRIGGER_CONDITION_MAP = {
    0: StartTriggerCondition_pb2.START_TRIGGER_CONDITION_TEST_START,
    1: StartTriggerCondition_pb2.START_TRIGGER_CONDITION_CHANNEL_VALUE_CHANGE,
    2: StartTriggerCondition_pb2.START_TRIGGER_CONDITION_TIME
}

START_TRIGGER_CONDITION_PB2_MAP = {
    StartTriggerCondition_pb2.START_TRIGGER_CONDITION_TEST_START: StartTriggerCondition.TEST_START,
    StartTriggerCondition_pb2.START_TRIGGER_CONDITION_CHANNEL_VALUE_CHANGE: StartTriggerCondition.CHANNEL_VALUE_CHANGE,
    StartTriggerCondition_pb2.START_TRIGGER_CONDITION_TIME: StartTriggerCondition.ABSOLUTE_TIME
}
