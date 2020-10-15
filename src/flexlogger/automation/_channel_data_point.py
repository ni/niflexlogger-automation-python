from datetime import datetime


class ChannelDataPoint:
    """The value for a channel at the specified timestamp."""

    def __init__(self, name: str, value: float, timestamp: datetime):
        self._name = name
        self._value = value
        self._timestamp = timestamp

    def __repr__(self) -> str:
        return 'flexlogger.automation.ChannelDataPoint("%s", %f, %s)' % (
            self._name,
            self._value,
            repr(self._timestamp),
        )

    @property
    def name(self) -> str:
        """The name of the channel."""
        return self._name

    @property
    def value(self) -> float:
        """The value of the channel."""
        return self._value

    @property
    def timestamp(self) -> datetime:
        """The timestamp when the value occurred."""
        return self._timestamp
