from typing import Any, List


class ChannelMetadata:
    """Display information about a channel, such as its unit, expected range, and data rate."""

    def __init__(
        self,
        channel_name: str,
        unit: str,
        expected_minimum: float,
        expected_maximum: float,
        actual_data_rate_hz: float,
        group_path: List[str],
        enabled: bool,
        writable: bool,
        data_type: str,
        errors: List[str],
        warnings: List[str],
    ) -> None:
        self._channel_name = channel_name
        self._unit = unit
        self._expected_minimum = expected_minimum
        self._expected_maximum = expected_maximum
        self._actual_data_rate_hz = actual_data_rate_hz
        self._group_path = group_path
        self._enabled = enabled
        self._writable = writable
        self._data_type = data_type
        self._errors = errors
        self._warnings = warnings

    @classmethod
    def _from_pb2(cls, channel_metadata_pb2: Any) -> "ChannelMetadata":
        return cls(
            channel_metadata_pb2.channel_name,
            channel_metadata_pb2.unit,
            channel_metadata_pb2.expected_minimum,
            channel_metadata_pb2.expected_maximum,
            channel_metadata_pb2.actual_data_rate_hz,
            list(channel_metadata_pb2.group_path),
            channel_metadata_pb2.enabled,
            channel_metadata_pb2.writable,
            channel_metadata_pb2.data_type,
            list(channel_metadata_pb2.errors),
            list(channel_metadata_pb2.warnings),
        )

    def __repr__(self) -> str:
        return "flexlogger.automation.ChannelMetadata(%s)" % repr(self._channel_name)

    @property
    def channel_name(self) -> str:
        """The name of the channel."""
        return self._channel_name

    @property
    def unit(self) -> str:
        """The unit of the channel, or an empty string if the channel has none."""
        return self._unit

    @property
    def expected_minimum(self) -> float:
        """The expected minimum value of the channel."""
        return self._expected_minimum

    @property
    def expected_maximum(self) -> float:
        """The expected maximum value of the channel."""
        return self._expected_maximum

    @property
    def actual_data_rate_hz(self) -> float:
        """The actual data rate of the channel in Hertz."""
        return self._actual_data_rate_hz

    @property
    def group_path(self) -> List[str]:
        """The groups that contain the channel in the I/O table, outermost first."""
        return self._group_path

    @property
    def enabled(self) -> bool:
        """Whether the channel is enabled."""
        return self._enabled

    @property
    def writable(self) -> bool:
        """Whether the value of the channel can be set through automation."""
        return self._writable

    @property
    def data_type(self) -> str:
        """The data type of the channel, for example ``"double"`` or ``"string"``."""
        return self._data_type

    @property
    def errors(self) -> List[str]:
        """The current errors of the channel."""
        return self._errors

    @property
    def warnings(self) -> List[str]:
        """The current warnings of the channel."""
        return self._warnings
