from enum import Enum
from .proto.ValueChangeType_pb2 import ValueChangeType as ValueChangeType_pb2


class ValueChangeType(Enum):
    """An enumeration describing the possible types of value change events."""

    """Start Trigger not configured."""
    NONE = 0

    """Start or stop a test when a channel value rises above a specified value."""
    RISE_ABOVE_VALUE = 1

    """Start or stop a test when a channel value falls below a specified value."""
    FALL_BELOW_VALUE = 3

    """Start or stop a test when a channel value enters a range."""
    ENTER_RANGE = 5

    """Start or stop a test when a channel value leaves a range."""
    LEAVE_RANGE = 6

    def to_value_change_type_pb2(self) -> ValueChangeType_pb2:
        return VALUE_CHANGE_TYPE_MAP.get(self.value)

    @staticmethod
    def from_value_change_type_pb2(value_change_type: ValueChangeType_pb2):
        return VALUE_CHANGE_TYPE_PB2_MAP.get(value_change_type)


VALUE_CHANGE_TYPE_MAP = {
    0: ValueChangeType_pb2.TYPE_NONE,
    1: ValueChangeType_pb2.TYPE_RISE_ABOVE_VALUE,
    2: ValueChangeType_pb2.TYPE_RISE_ABOVE_VALUE_INCLUSIVE,
    3: ValueChangeType_pb2.TYPE_FALL_BELOW_VALUE,
    4: ValueChangeType_pb2.TYPE_FALL_BELOW_VALUE_INCLUSIVE,
    5: ValueChangeType_pb2.TYPE_ENTER_RANGE,
    6: ValueChangeType_pb2.TYPE_LEAVE_RANGE
}

VALUE_CHANGE_TYPE_PB2_MAP = {
    ValueChangeType_pb2.TYPE_NONE: ValueChangeType.NONE,
    ValueChangeType_pb2.TYPE_RISE_ABOVE_VALUE: ValueChangeType.RISE_ABOVE_VALUE,
    ValueChangeType_pb2.TYPE_FALL_BELOW_VALUE: ValueChangeType.FALL_BELOW_VALUE,
    ValueChangeType_pb2.TYPE_ENTER_RANGE: ValueChangeType.ENTER_RANGE,
    ValueChangeType_pb2.TYPE_LEAVE_RANGE: ValueChangeType.LEAVE_RANGE
}
