from ._value_change_type import ValueChangeType
import json


class ValueChangeCondition:
    """Represents a value change condition.
     Create a ValueChangeCondition object when you want to set the start or stop trigger to value change.
    """

    def __init__(self, value_change_condition='') -> None:
        if len(value_change_condition) > 0:
            json_condition = json.loads(value_change_condition)
            self._channel_name = json_condition['ChannelName']
            self._value_change_type = ValueChangeType.from_value_change_type_pb2(int(json_condition['ValueChangeType']))
            self._threshold = float(json_condition['Threshold'])
            self._min_value = float(json_condition['MinValue'])
            self._max_value = float(json_condition['MaxValue'])
            self._time = float(json_condition['Time'])
        else:
            self._channel_name = ''
            self._value_change_type = ValueChangeType.NONE
            self._threshold = 0
            self._min_value = 0
            self._max_value = 0
            self._time = 0

    def __eq__(self, other):
        objects_equal = (self._channel_name == other.channel_name and
                         self._value_change_type == other.value_change_type and
                         self._threshold == other.threshold and
                         self._min_value == other.min_value and
                         self._max_value == other.max_value and
                         self._time == other.time)
        return objects_equal

    def __repr__(self):
        value_change_condition_string = 'ValueChangeCondition\r\n' \
                                        'channel_name = {0}\r\n' \
                                        'value_change_type = {1}\r\n' \
                                        'threshold = {2}\r\n' \
                                        'min_value = {3}\r\n' \
                                        'max_value = {4}\r\n' \
                                        'time = {5}'.format(self._channel_name,
                                                            self._value_change_type,
                                                            self._threshold,
                                                            self._min_value,
                                                            self._max_value,
                                                            self._time)
        return value_change_condition_string

    @property
    def channel_name(self) -> str:
        """The channel name."""
        return self._channel_name

    @channel_name.setter
    def channel_name(self, value: str):
        self._channel_name = value

    @property
    def value_change_type(self) -> ValueChangeType:
        """The value change type."""
        return self._value_change_type

    @value_change_type.setter
    def value_change_type(self, value: ValueChangeType):
        self._value_change_type = value

    @property
    def threshold(self) -> float:
        """The threshold."""
        return self._threshold

    @threshold.setter
    def threshold(self, value: float):
        self._threshold = value

    @property
    def min_value(self) -> float:
        """The range minimum."""
        return self._min_value

    @min_value.setter
    def min_value(self, value: float):
        self._min_value = value

    @property
    def max_value(self) -> float:
        """The range maximum."""
        return self._max_value

    @max_value.setter
    def max_value(self, value: float):
        self._max_value = value

    @property
    def time(self) -> float:
        """The leading or trailing time in seconds."""
        return self._time

    @time.setter
    def time(self, value: float):
        self._time = value
