import threading
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, Generic, List, NoReturn, Optional, Sequence, TypeVar

from grpc import RpcError, StatusCode

from ._channel_data_point import ChannelDataPoint
from ._channel_metadata import ChannelMetadata
from ._flexlogger_error import FlexLoggerError
from .proto import ChannelDataStream_pb2

_FrameT = TypeVar("_FrameT")
_StreamT = TypeVar("_StreamT", bound="_ChannelDataStreamBase[Any]")


def _to_utc_datetime(timestamp_pb2: Any) -> datetime:
    return timestamp_pb2.ToDatetime().replace(tzinfo=timezone.utc)


class WindowStatistics:
    """The minimum, maximum, and average of a channel over the window of a frame."""

    def __init__(self, minimum: float, maximum: float, average: float) -> None:
        self._minimum = minimum
        self._maximum = maximum
        self._average = average

    def __repr__(self) -> str:
        return "flexlogger.automation.WindowStatistics(%f, %f, %f)" % (
            self._minimum,
            self._maximum,
            self._average,
        )

    @property
    def minimum(self) -> float:
        """The minimum value in the window."""
        return self._minimum

    @property
    def maximum(self) -> float:
        """The maximum value in the window."""
        return self._maximum

    @property
    def average(self) -> float:
        """The average value in the window."""
        return self._average


class ChannelFrame:
    """The data of one channel in a :class:`StreamFrame`.

    FlexLogger reduces the window to minimum and maximum values, like the FlexLogger high speed
    graph. Each bin contributes its minimum and maximum at the times they occurred, so the points
    are not evenly spaced. Plot ``times_seconds`` against ``values`` as one line to see every peak.
    """

    def __init__(
        self,
        name: str,
        reference_time: datetime,
        times_seconds: List[float],
        values: List[float],
        statistics: Optional[WindowStatistics],
        latest: Optional[ChannelDataPoint],
    ) -> None:
        self._name = name
        self._reference_time = reference_time
        self._times_seconds = times_seconds
        self._values = values
        self._statistics = statistics
        self._latest = latest

    @classmethod
    def _from_pb2(cls, channel_frame_pb2: Any, reference_time: datetime) -> "ChannelFrame":
        statistics = None
        if channel_frame_pb2.HasField("statistics"):
            statistics = WindowStatistics(
                channel_frame_pb2.statistics.minimum,
                channel_frame_pb2.statistics.maximum,
                channel_frame_pb2.statistics.average,
            )
        latest = None
        if channel_frame_pb2.HasField("latest"):
            latest = ChannelDataPoint(
                channel_frame_pb2.channel_name,
                channel_frame_pb2.latest.value,
                _to_utc_datetime(channel_frame_pb2.latest.timestamp),
            )
        return cls(
            channel_frame_pb2.channel_name,
            reference_time,
            list(channel_frame_pb2.min_max.time_offsets),
            list(channel_frame_pb2.min_max.values),
            statistics,
            latest,
        )

    def __repr__(self) -> str:
        return "flexlogger.automation.ChannelFrame(%s, %d points)" % (
            repr(self._name),
            len(self._values),
        )

    @property
    def name(self) -> str:
        """The name of the channel."""
        return self._name

    @property
    def times_seconds(self) -> List[float]:
        """The time of each point in seconds, relative to :attr:`StreamFrame.reference_time`."""
        return self._times_seconds

    @property
    def values(self) -> List[float]:
        """The value of each point."""
        return self._values

    @property
    def statistics(self) -> Optional[WindowStatistics]:
        """The statistics of the window, or None if they were not requested."""
        return self._statistics

    @property
    def latest(self) -> Optional[ChannelDataPoint]:
        """The latest value of the channel, or None if it was not requested."""
        return self._latest

    def timestamps(self) -> List[datetime]:
        """Get the time of each point as a timezone-aware UTC datetime."""
        return [self._reference_time + timedelta(seconds=offset) for offset in self._times_seconds]


class StreamFrame:
    """A snapshot of the visible window of every streamed channel.

    Each frame replaces the previous one. Frames overlap, and FlexLogger skips frames when the
    client reads too slowly.
    """

    def __init__(
        self,
        sequence_number: int,
        reference_time: datetime,
        channels: Dict[str, ChannelFrame],
        dropped_frames_total: int,
    ) -> None:
        self._sequence_number = sequence_number
        self._reference_time = reference_time
        self._channels = channels
        self._dropped_frames_total = dropped_frames_total

    @classmethod
    def _from_pb2(cls, frame_pb2: Any) -> "StreamFrame":
        reference_time = _to_utc_datetime(frame_pb2.reference_time)
        channels = {}
        for channel_frame_pb2 in frame_pb2.channels:
            channels[channel_frame_pb2.channel_name] = ChannelFrame._from_pb2(
                channel_frame_pb2, reference_time
            )
        return cls(
            frame_pb2.sequence_number, reference_time, channels, frame_pb2.dropped_frames_total
        )

    def __repr__(self) -> str:
        return "flexlogger.automation.StreamFrame(%d)" % self._sequence_number

    @property
    def sequence_number(self) -> int:
        """The number of the frame, which increases by one for each frame FlexLogger sends."""
        return self._sequence_number

    @property
    def reference_time(self) -> datetime:
        """The timezone-aware UTC time that the times of the channel points are relative to."""
        return self._reference_time

    @property
    def channels(self) -> Dict[str, ChannelFrame]:
        """The data of each streamed channel, keyed by channel name."""
        return self._channels

    @property
    def dropped_frames_total(self) -> int:
        """The total number of frames FlexLogger skipped because the client read too slowly."""
        return self._dropped_frames_total


class _ChannelDataStreamBase(Generic[_FrameT]):
    """Reads a channel data stream: the start message, frames, cancellation, and errors.

    Subclasses turn each frame message into their own frame type in :meth:`_parse_frame`.
    """

    def __init__(
        self,
        responses: Any,
        raise_if_application_closed: Callable[[], None],
        accepted_modes: Sequence[int],
        mode_error_message: str,
    ) -> None:
        self._responses = responses
        self._raise_if_application_closed = raise_if_application_closed
        self._mode_error_message = mode_error_message
        self._is_cancelled = False
        self._lock = threading.Lock()
        self._latest_frame = None  # type: Optional[_FrameT]
        self._background_thread = None  # type: Optional[threading.Thread]
        self._background_error = None  # type: Optional[Exception]

        started = self._read_message()
        if started is None or started.WhichOneof("message") != "started":
            self.cancel()
            raise FlexLoggerError("The channel data stream did not start as expected.")
        # A server that does not know the requested mode ignores it, so a mismatch means the
        # server is too old to provide the requested kind of frames.
        if started.started.effective_mode not in accepted_modes:
            self.cancel()
            raise FlexLoggerError(mode_error_message)
        self._metadata = [
            ChannelMetadata._from_pb2(channel) for channel in started.started.channels
        ]

    def __enter__(self: _StreamT) -> _StreamT:
        return self

    def __exit__(self, *args: Any) -> None:
        self.cancel()

    def __iter__(self: _StreamT) -> _StreamT:
        return self

    def __next__(self) -> _FrameT:
        while True:
            message = self._read_message()
            if message is None:
                raise StopIteration
            if message.WhichOneof("message") == "frame":
                frame = self._parse_frame(message.frame)
                with self._lock:
                    self._latest_frame = frame
                return frame

    @property
    def metadata(self) -> List[ChannelMetadata]:
        """The metadata of each streamed channel, in the order the channels were requested."""
        return self._metadata

    def cancel(self) -> None:
        """Stop the stream. Iteration over the stream ends without an error."""
        self._is_cancelled = True
        self._responses.cancel()

    def _parse_frame(self, frame_pb2: Any) -> _FrameT:
        raise NotImplementedError()

    def _get_latest_frame(self) -> Optional[_FrameT]:
        with self._lock:
            if self._background_error is not None:
                raise self._background_error
            return self._latest_frame

    def _start_background(self, callback: Optional[Callable[[_FrameT], None]]) -> None:
        if self._background_thread is not None:
            raise RuntimeError("The stream already runs in the background.")
        self._background_thread = threading.Thread(
            target=self._run_background, args=(callback,), daemon=True
        )
        self._background_thread.start()

    def _run_background(self, callback: Optional[Callable[[_FrameT], None]]) -> None:
        try:
            for frame in self:
                if callback is not None:
                    callback(frame)
        except Exception as error:
            with self._lock:
                self._background_error = error
            self.cancel()

    def _read_message(self) -> Optional[Any]:
        try:
            return next(self._responses)
        except StopIteration:
            return None
        except RpcError as error:
            if self._is_cancelled:
                return None
            self._raise_flexlogger_error(error)

    def _raise_flexlogger_error(self, error: RpcError) -> NoReturn:
        code = error.code() if hasattr(error, "code") else None
        if code == StatusCode.UNIMPLEMENTED:
            raise FlexLoggerError(self._mode_error_message) from error
        self._raise_if_application_closed()
        if code == StatusCode.UNAVAILABLE:
            raise FlexLoggerError(
                "The channel data stream ended because FlexLogger stopped providing data"
            ) from error
        raise FlexLoggerError("Failed to stream channel data") from error


class ChannelDataStream(_ChannelDataStreamBase[StreamFrame]):
    """A live stream of channel data from FlexLogger.

    Do not create this class directly; instead, use the return value of
    :meth:`.ChannelSpecificationDocument.stream_channel_data`.

    Use the stream as a context manager so it is cancelled when you are done. Iterate over it to
    receive each :class:`StreamFrame`, or call :meth:`start_background` and read
    :attr:`latest_frame` from code that cannot block.
    """

    def __init__(self, responses: Any, raise_if_application_closed: Callable[[], None]) -> None:
        super().__init__(
            responses,
            raise_if_application_closed,
            (
                ChannelDataStream_pb2.STREAM_MODE_UNSPECIFIED,
                ChannelDataStream_pb2.STREAM_MODE_DISPLAY,
            ),
            "Streaming channel data requires a newer version of FlexLogger.",
        )

    @property
    def latest_frame(self) -> Optional[StreamFrame]:
        """The most recent frame received, or None if no frame has arrived yet.

        This is safe to read from any thread.

        Raises:
            FlexLoggerError: if the stream running in the background failed.
        """
        return self._get_latest_frame()

    def start_background(self, callback: Optional[Callable[[StreamFrame], None]] = None) -> None:
        """Receive frames on a worker thread instead of by iterating.

        Read the most recent frame from :attr:`latest_frame`. Call this at most once, and do not
        also iterate over the stream.

        Args:
            callback: An optional function to call with each frame on the worker thread.

        Raises:
            RuntimeError: if the stream already runs in the background.
        """
        self._start_background(callback)

    def _parse_frame(self, frame_pb2: Any) -> StreamFrame:
        return StreamFrame._from_pb2(frame_pb2)
