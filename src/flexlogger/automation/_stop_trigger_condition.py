from enum import Enum
from .proto.StopTriggerCondition_pb2 import StopTriggerCondition as StopTriggerCondition_pb2


class StopTriggerCondition(Enum):
    """An enumeration describing when to the logging stops."""

    """Manually stop logging by clicking the STOP button."""
    TEST_STOP = 0

    """Stop logging when the value of the acquisition on a designated channel meets the specified value change condition."""
    CHANNEL_VALUE_CHANGE = 1

    """Stop logging after a designated duration of time has elapsed."""
    TEST_TIME_ELAPSED = 2

    def to_stop_trigger_condition_pb2(self) -> StopTriggerCondition_pb2:
        return STOP_TRIGGER_CONDITION_MAP.get(self.value)

    @staticmethod
    def from_stop_trigger_condition_pb2(stop_trigger_condition: StopTriggerCondition_pb2):
        return STOP_TRIGGER_CONDITION_PB2_MAP.get(stop_trigger_condition)


STOP_TRIGGER_CONDITION_MAP = {
    0: StopTriggerCondition_pb2.STOP_TRIGGER_CONDITION_TEST_STOP,
    1: StopTriggerCondition_pb2.STOP_TRIGGER_CONDITION_CHANNEL_VALUE_CHANGE,
    2: StopTriggerCondition_pb2.STOP_TRIGGER_CONDITION_TIME_ELAPSED
}

STOP_TRIGGER_CONDITION_PB2_MAP = {
    StopTriggerCondition_pb2.STOP_TRIGGER_CONDITION_TEST_STOP: StopTriggerCondition.TEST_STOP,
    StopTriggerCondition_pb2.STOP_TRIGGER_CONDITION_CHANNEL_VALUE_CHANGE: StopTriggerCondition.CHANNEL_VALUE_CHANGE,
    StopTriggerCondition_pb2.STOP_TRIGGER_CONDITION_TIME_ELAPSED: StopTriggerCondition.TEST_TIME_ELAPSED
}
