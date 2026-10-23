from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from ._channel_data_stream import _ChannelDataStreamBase, _to_utc_datetime
from ._flexlogger_error import FlexLoggerError
from .proto import ChannelDataStream_pb2


class SampleSegment:
    """A run of consecutive samples of one channel in a :class:`RawStreamFrame`.

    Evenly spaced samples have a :attr:`sample_interval_seconds`. Individually timed samples
    have none and carry their own times instead.
    """

    def __init__(
        self,
        values: List[float],
        follows_gap: bool,
        start_offset_seconds: float,
        sample_interval_seconds: Optional[float],
        times_seconds: Optional[List[float]] = None,
    ) -> None:
        self._values = values
        self._follows_gap = follows_gap
        self._start_offset_seconds = start_offset_seconds
        self._sample_interval_seconds = sample_interval_seconds
        self._times_seconds = times_seconds

    @classmethod
    def _from_pb2(cls, segment_pb2: Any, channel_name: str) -> "SampleSegment":
        values = list(segment_pb2.values)
        if len(values) == 0:
            raise FlexLoggerError(
                "FlexLogger sent a sample segment without values for channel '%s'." % channel_name
            )
        timing = segment_pb2.WhichOneof("timing")
        if timing == "uniform":
            sample_interval = segment_pb2.uniform.sample_interval
            if not sample_interval > 0:
                raise FlexLoggerError(
                    "FlexLogger sent a sample interval of %r seconds for channel '%s'."
                    % (sample_interval, channel_name)
                )
            return cls(
                values, segment_pb2.follows_gap, segment_pb2.uniform.start_offset, sample_interval
            )
        if timing == "times":
            times_seconds = list(segment_pb2.times.time_offsets)
            if len(times_seconds) != len(values):
                raise FlexLoggerError(
                    "FlexLogger sent %d sample times for %d values of channel '%s'."
                    % (len(times_seconds), len(values), channel_name)
                )
            return cls(values, segment_pb2.follows_gap, times_seconds[0], None, times_seconds)
        raise FlexLoggerError(
            "FlexLogger sent a sample segment without timing for channel '%s'." % channel_name
        )

    def __repr__(self) -> str:
        return "flexlogger.automation.SampleSegment(%d samples)" % len(self._values)

    @property
    def start_offset_seconds(self) -> float:
        """The time of the first sample in seconds, relative to the frame reference time."""
        return self._start_offset_seconds

    @property
    def sample_interval_seconds(self) -> Optional[float]:
        """The seconds between samples, or None if the samples are individually timed."""
        return self._sample_interval_seconds

    @property
    def values(self) -> List[float]:
        """The value of each sample, in time order."""
        return self._values

    @property
    def follows_gap(self) -> bool:
        """Whether samples are missing between the previous segment of the channel and this one.

        FlexLogger discards samples it keeps no longer when the client reads too slowly.
        """
        return self._follows_gap

    @property
    def times_seconds(self) -> List[float]:
        """The time of each sample in seconds, relative to :attr:`RawStreamFrame.reference_time`."""
        if self._times_seconds is None:
            start = self._start_offset_seconds
            interval = self._sample_interval_seconds or 0.0
            # Multiplying instead of adding up the interval keeps rounding errors from growing.
            self._times_seconds = [start + index * interval for index in range(len(self._values))]
        return self._times_seconds


class ChannelSamples:
    """The samples of one channel in a :class:`RawStreamFrame`.

    The samples are the ones the channel acquired since the previous frame, so they continue the
    samples of the previous frame. A channel without new samples has no segments.
    """

    def __init__(self, name: str, reference_time: datetime, segments: List[SampleSegment]) -> None:
        self._name = name
        self._reference_time = reference_time
        self._segments = segments
        self._values = None  # type: Optional[List[float]]
        self._times_seconds = None  # type: Optional[List[float]]

    @classmethod
    def _from_pb2(cls, channel_frame_pb2: Any, reference_time: datetime) -> "ChannelSamples":
        name = channel_frame_pb2.channel_name
        data = channel_frame_pb2.WhichOneof("data")
        if data is not None and data != "samples":
            raise FlexLoggerError(
                "FlexLogger sent data other than samples for channel '%s' in a raw stream." % name
            )
        segments = [
            SampleSegment._from_pb2(segment_pb2, name)
            for segment_pb2 in channel_frame_pb2.samples.segments
        ]
        return cls(name, reference_time, segments)

    def __repr__(self) -> str:
        return "flexlogger.automation.ChannelSamples(%s, %d samples)" % (
            repr(self._name),
            len(self),
        )

    def __len__(self) -> int:
        return sum(len(segment.values) for segment in self._segments)

    @property
    def name(self) -> str:
        """The name of the channel."""
        return self._name

    @property
    def segments(self) -> List[SampleSegment]:
        """The runs of samples, in time order."""
        return self._segments

    @property
    def values(self) -> List[float]:
        """The value of each new sample of all segments, in time order."""
        if self._values is None:
            self._values = [value for segment in self._segments for value in segment.values]
        return self._values

    @property
    def times_seconds(self) -> List[float]:
        """The time of each value in seconds, relative to :attr:`RawStreamFrame.reference_time`."""
        if self._times_seconds is None:
            self._times_seconds = [
                time for segment in self._segments for time in segment.times_seconds
            ]
        return self._times_seconds

    @property
    def has_gap(self) -> bool:
        """Whether samples are missing before any segment of the channel in this frame."""
        return any(segment.follows_gap for segment in self._segments)

    def timestamps(self) -> List[datetime]:
        """Get the time of each value as a timezone-aware UTC datetime.

        Datetimes have a resolution of one microsecond. Use :attr:`times_seconds` for more
        precision.
        """
        return [self._reference_time + timedelta(seconds=offset) for offset in self.times_seconds]


class RawStreamFrame:
    """The samples every streamed channel acquired since the previous frame.

    Frames follow each other: append the samples of each frame to rebuild the signal of each
    channel. FlexLogger never skips a frame.
    """

    def __init__(
        self,
        sequence_number: int,
        reference_time: datetime,
        channels: Dict[str, ChannelSamples],
    ) -> None:
        self._sequence_number = sequence_number
        self._reference_time = reference_time
        self._channels = channels

    @classmethod
    def _from_pb2(cls, frame_pb2: Any) -> "RawStreamFrame":
        reference_time = _to_utc_datetime(frame_pb2.reference_time)
        channels = {}
        for channel_frame_pb2 in frame_pb2.channels:
            channels[channel_frame_pb2.channel_name] = ChannelSamples._from_pb2(
                channel_frame_pb2, reference_time
            )
        return cls(frame_pb2.sequence_number, reference_time, channels)

    def __repr__(self) -> str:
        return "flexlogger.automation.RawStreamFrame(%d)" % self._sequence_number

    @property
    def sequence_number(self) -> int:
        """The number of the frame, which increases by one for each frame FlexLogger sends."""
        return self._sequence_number

    @property
    def reference_time(self) -> datetime:
        """The timezone-aware UTC time that the times of the samples are relative to.

        This is the time of the earliest sample in the frame.
        """
        return self._reference_time

    @property
    def channels(self) -> Dict[str, ChannelSamples]:
        """The samples of each streamed channel, keyed by channel name, in request order."""
        return self._channels


class RawChannelDataStream(_ChannelDataStreamBase[RawStreamFrame]):
    """A stream of every sample of channels from FlexLogger.

    Do not create this class directly; instead, use the return value of
    :meth:`.ChannelSpecificationDocument.stream_raw_channel_data`.

    Use the stream as a context manager so it is cancelled when you are done. Iterate over it to
    receive each :class:`RawStreamFrame`, or call :meth:`start_background` with a callback.
    Each frame holds only the samples since the previous frame, so process every frame to see
    every sample.

    Raises:
        FlexLoggerError: while iterating, if the stream fails or FlexLogger sends data that the
            client cannot read.
    """

    def __init__(self, responses: Any, raise_if_application_closed: Callable[[], None]) -> None:
        super().__init__(
            responses,
            raise_if_application_closed,
            (ChannelDataStream_pb2.STREAM_MODE_RAW,),
            "Streaming raw channel data requires a newer version of FlexLogger.",
        )

    @property
    def latest_frame(self) -> Optional[RawStreamFrame]:
        """The most recent frame received, or None if no frame has arrived yet.

        This holds only the newest frame, so reading it misses the samples of earlier frames.
        Pass a callback to :meth:`start_background` to receive every sample. This is safe to read
        from any thread.

        Raises:
            FlexLoggerError: if the stream running in the background failed.
        """
        return self._get_latest_frame()

    def start_background(self, callback: Optional[Callable[[RawStreamFrame], None]] = None) -> None:
        """Receive frames on a worker thread instead of by iterating.

        Only the callback receives every frame; :attr:`latest_frame` holds the newest frame only.
        Call this at most once, and do not also iterate over the stream. The callback runs on the
        worker thread. Keep it short: while it runs, FlexLogger holds back new samples, and it
        discards samples older than its history, which shows up as a gap.

        Args:
            callback: An optional function to call with each frame on the worker thread.

        Raises:
            RuntimeError: if the stream already runs in the background.
        """
        self._start_background(callback)

    def _parse_frame(self, frame_pb2: Any) -> RawStreamFrame:
        return RawStreamFrame._from_pb2(frame_pb2)
