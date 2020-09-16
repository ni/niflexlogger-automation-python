from datetime import datetime


class ChannelDataPoint:
    """The value for a channel that occurred at the specified timestamp."""

    def __init__(self, channel_name: str, channel_value: float, timestamp: datetime):
        self._channel_name = channel_name
        self._channel_value = channel_value
        self._timestamp = timestamp

    @property
    def channel_name(self) -> str:
        """The name of the channel."""
        return self._channel_name

    @property
    def channel_value(self) -> float:
        """The value of the channel."""
        return self._channel_value

    @property
    def timestamp(self) -> datetime:
        """The timestamp when the value occurred."""
        return self._timestamp
