import threading
import time
from datetime import datetime, timedelta, timezone

import grpc
import pytest
from flexlogger.automation import FlexLoggerError
from flexlogger.automation.proto import ChannelDataStream_pb2
from google.protobuf.timestamp_pb2 import Timestamp

REFERENCE_TIME = datetime(2026, 10, 2, 12, 0, 0, tzinfo=timezone.utc)


def _timestamp(value):
    timestamp = Timestamp()
    timestamp.FromDatetime(value.replace(tzinfo=None))
    return timestamp


def _channel_metadata(name, unit="V"):
    return ChannelDataStream_pb2.ChannelMetadata(
        channel_name=name,
        unit=unit,
        expected_minimum=-10.0,
        expected_maximum=10.0,
        actual_data_rate_hz=1000.0,
        group_path=["Group", "Subgroup"],
        enabled=True,
        writable=False,
        data_type="double",
    )


def _started(*channel_names):
    return ChannelDataStream_pb2.StreamChannelDataResponse(
        started=ChannelDataStream_pb2.StreamStarted(
            channels=[_channel_metadata(name) for name in channel_names]
        )
    )


def _channel_frame(name, time_offsets, values, statistics=None, latest=None):
    channel_frame = ChannelDataStream_pb2.ChannelFrame(
        channel_name=name,
        min_max=ChannelDataStream_pb2.MinMaxSeries(time_offsets=time_offsets, values=values),
    )
    if statistics is not None:
        channel_frame.statistics.CopyFrom(statistics)
    if latest is not None:
        channel_frame.latest.CopyFrom(latest)
    return channel_frame


def _frame(sequence_number, *channel_frames, dropped_frames_total=0):
    return ChannelDataStream_pb2.StreamChannelDataResponse(
        frame=ChannelDataStream_pb2.DataFrame(
            sequence_number=sequence_number,
            reference_time=_timestamp(REFERENCE_TIME),
            channels=channel_frames,
            dropped_frames_total=dropped_frames_total,
        )
    )


def _status(code, channel_name="", message=""):
    return ChannelDataStream_pb2.StreamChannelDataResponse(
        status=ChannelDataStream_pb2.StreamStatus(
            code=code, channel_name=channel_name, message=message
        )
    )


def _wait_for_flexlogger_error(read):
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        try:
            read()
        except FlexLoggerError as error:
            return error
        time.sleep(0.01)
    pytest.fail("Expected a FlexLoggerError but none was raised.")


def test___started_then_frames___iterate___yields_frames_with_metadata(
    servicer, channel_specification_document
):
    servicer.stream_messages = [
        _started("Sine 1", "Sine 2"),
        _frame(
            1,
            _channel_frame("Sine 1", [0.0, 0.5], [0.0, 1.0]),
            _channel_frame("Sine 2", [0.0, 0.5], [2.0, 3.0]),
        ),
        _frame(
            2,
            _channel_frame("Sine 1", [0.5, 1.0], [1.0, 0.0]),
            _channel_frame("Sine 2", [0.5, 1.0], [3.0, 2.0]),
            dropped_frames_total=4,
        ),
    ]

    with channel_specification_document.stream_channel_data(["Sine 1", "Sine 2"]) as stream:
        frames = list(stream)

    assert [channel.channel_name for channel in stream.metadata] == ["Sine 1", "Sine 2"]
    assert stream.metadata[0].unit == "V"
    assert [frame.sequence_number for frame in frames] == [1, 2]
    assert frames[0].channels["Sine 2"].values == [2.0, 3.0]
    assert frames[1].channels["Sine 1"].times_seconds == [0.5, 1.0]
    assert [frame.dropped_frames_total for frame in frames] == [0, 4]


def test___open_stream___cancel___iteration_ends_without_error(
    servicer, channel_specification_document
):
    servicer.stream_messages = [_started("Sine 1")]
    servicer.keep_stream_open = True
    errors = []
    iteration_finished = threading.Event()
    stream = channel_specification_document.stream_channel_data(["Sine 1"])

    def iterate():
        try:
            for _ in stream:
                pass
        except Exception as error:
            errors.append(error)
        iteration_finished.set()

    threading.Thread(target=iterate, daemon=True).start()
    stream.cancel()

    assert iteration_finished.wait(5)
    assert errors == []
    assert servicer.client_disconnected.wait(5)


def test___server_unimplemented___stream___raises_flexlogger_error_requiring_newer_version(
    servicer, channel_specification_document
):
    servicer.abort_status = (grpc.StatusCode.UNIMPLEMENTED, "Method not found!")

    with pytest.raises(FlexLoggerError) as error_info:
        channel_specification_document.stream_channel_data(["Sine 1"])

    assert "requires a newer version of FlexLogger" in str(error_info.value)


def test___invalid_argument___stream___raises_flexlogger_error_with_code(
    servicer, channel_specification_document
):
    servicer.abort_status = (
        grpc.StatusCode.INVALID_ARGUMENT,
        "[-143040] The channel Missing was not found.",
    )

    with pytest.raises(FlexLoggerError) as error_info:
        channel_specification_document.stream_channel_data(["Missing"])

    assert error_info.value.error_code == -143040


def test___resource_exhausted___stream___raises_flexlogger_error(
    servicer, channel_specification_document
):
    servicer.abort_status = (grpc.StatusCode.RESOURCE_EXHAUSTED, "Too many streams.")

    with pytest.raises(FlexLoggerError):
        channel_specification_document.stream_channel_data(["Sine 1"])


def test___first_message_is_a_frame___stream___raises_flexlogger_error(
    servicer, channel_specification_document
):
    servicer.stream_messages = [_frame(1)]

    with pytest.raises(FlexLoggerError):
        channel_specification_document.stream_channel_data(["Sine 1"])


def test___background_mode___frames_arrive___latest_frame_updates_and_callback_called(
    servicer, channel_specification_document
):
    servicer.stream_messages = [
        _started("Sine 1"),
        _frame(1, _channel_frame("Sine 1", [0.0], [0.0])),
        _frame(2, _channel_frame("Sine 1", [0.0], [1.0])),
        _frame(3, _channel_frame("Sine 1", [0.0], [2.0])),
    ]
    servicer.keep_stream_open = True
    received = []
    all_received = threading.Event()

    def on_frame(frame):
        received.append(frame.sequence_number)
        if len(received) == 3:
            all_received.set()

    with channel_specification_document.stream_channel_data(["Sine 1"]) as stream:
        stream.start_background(on_frame)

        assert all_received.wait(5)
        assert received == [1, 2, 3]
        assert stream.latest_frame.sequence_number == 3
        assert stream.latest_frame.channels["Sine 1"].values == [2.0]


def test___background_mode_without_frames___latest_frame___is_none(
    servicer, channel_specification_document
):
    servicer.stream_messages = [_started("Sine 1")]
    servicer.keep_stream_open = True

    with channel_specification_document.stream_channel_data(["Sine 1"]) as stream:
        stream.start_background()

        assert stream.latest_frame is None


def test___background_mode_started___start_background_again___raises_runtime_error(
    servicer, channel_specification_document
):
    servicer.stream_messages = [_started("Sine 1")]
    servicer.keep_stream_open = True

    with channel_specification_document.stream_channel_data(["Sine 1"]) as stream:
        stream.start_background()

        with pytest.raises(RuntimeError):
            stream.start_background()


def test___background_mode_server_unavailable___latest_frame___raises_flexlogger_error(
    servicer, channel_specification_document
):
    servicer.stream_messages = [_started("Sine 1")]
    servicer.abort_status = (grpc.StatusCode.UNAVAILABLE, "The project was closed.")

    with channel_specification_document.stream_channel_data(["Sine 1"]) as stream:
        stream.start_background()

        _wait_for_flexlogger_error(lambda: stream.latest_frame)


def test___frame_offsets___timestamps___returns_reference_time_plus_offsets(
    servicer, channel_specification_document
):
    servicer.stream_messages = [
        _started("Sine 1"),
        _frame(1, _channel_frame("Sine 1", [-1.0, 0.0, 0.25], [5.0, 6.0, 7.0])),
    ]

    with channel_specification_document.stream_channel_data(["Sine 1"]) as stream:
        frame = next(iter(stream))

    assert frame.reference_time == REFERENCE_TIME
    assert frame.channels["Sine 1"].timestamps() == [
        REFERENCE_TIME - timedelta(seconds=1),
        REFERENCE_TIME,
        REFERENCE_TIME + timedelta(milliseconds=250),
    ]


def test___frame_with_statistics_and_latest_value___iterate___exposes_them(
    servicer, channel_specification_document
):
    statistics = ChannelDataStream_pb2.WindowStatistics(minimum=-1.0, maximum=3.0, average=0.5)
    latest = ChannelDataStream_pb2.LatestValue(value=2.5, timestamp=_timestamp(REFERENCE_TIME))
    servicer.stream_messages = [
        _started("Sine 1", "Sine 2"),
        _frame(
            1,
            _channel_frame("Sine 1", [0.0], [2.5], statistics=statistics, latest=latest),
            _channel_frame("Sine 2", [0.0], [1.0]),
        ),
    ]

    with channel_specification_document.stream_channel_data(
        ["Sine 1", "Sine 2"], include_statistics=True, include_latest_value=True
    ) as stream:
        frame = next(iter(stream))

    with_extras = frame.channels["Sine 1"]
    assert (with_extras.statistics.minimum, with_extras.statistics.maximum) == (-1.0, 3.0)
    assert with_extras.statistics.average == 0.5
    assert (with_extras.latest.name, with_extras.latest.value) == ("Sine 1", 2.5)
    assert with_extras.latest.timestamp == REFERENCE_TIME
    assert frame.channels["Sine 2"].statistics is None
    assert frame.channels["Sine 2"].latest is None


def test___status_messages_between_frames___iterate___yields_only_frames(
    servicer, channel_specification_document
):
    servicer.stream_messages = [
        _started("Sine 1"),
        _status(ChannelDataStream_pb2.STREAM_STATUS_CODE_HEARTBEAT),
        _frame(1, _channel_frame("Sine 1", [0.0], [0.0])),
        _status(ChannelDataStream_pb2.STREAM_STATUS_CODE_CHANNEL_ERROR, "Sine 1", "No data."),
        _frame(2, _channel_frame("Sine 1", [0.0], [1.0])),
    ]

    with channel_specification_document.stream_channel_data(["Sine 1"]) as stream:
        frames = list(stream)

    assert [frame.sequence_number for frame in frames] == [1, 2]


def test___stream_parameters___stream___sends_them_in_the_request(
    servicer, channel_specification_document
):
    servicer.stream_messages = [_started("Sine 1", "Sine 2")]

    with channel_specification_document.stream_channel_data(
        ["Sine 1", "Sine 2"],
        window_seconds=10.0,
        points_per_window=800,
        max_update_rate_hz=5.0,
        include_statistics=True,
        include_latest_value=True,
    ):
        pass

    request = servicer.stream_requests[0]
    assert request.document_identifier.project_id == "project"
    assert request.document_identifier.file_name == "channels.lcspec"
    assert list(request.channel_names) == ["Sine 1", "Sine 2"]
    assert request.window_seconds == 10.0
    assert request.points_per_window == 800
    assert request.max_update_rate_hz == 5.0
    assert request.include_statistics
    assert request.include_latest_value


def test___no_stream_parameters___stream___requests_server_defaults(
    servicer, channel_specification_document
):
    servicer.stream_messages = [_started("Sine 1")]

    with channel_specification_document.stream_channel_data(["Sine 1"]):
        pass

    request = servicer.stream_requests[0]
    assert request.window_seconds == 0.0
    assert request.points_per_window == 0
    assert request.max_update_rate_hz == 0.0
    assert not request.include_statistics
    assert not request.include_latest_value


def test___stream_interrupted_by_server_unavailable___iterate___raises_flexlogger_error(
    servicer, channel_specification_document
):
    servicer.stream_messages = [_started("Sine 1"), _frame(1)]
    servicer.abort_status = (grpc.StatusCode.UNAVAILABLE, "The project was closed.")

    with channel_specification_document.stream_channel_data(["Sine 1"]) as stream:
        iterator = iter(stream)
        assert next(iterator).sequence_number == 1

        with pytest.raises(FlexLoggerError):
            next(iterator)


def test___application_closed___stream_interrupted___iterate___raises_application_closed_error(
    servicer, channel_specification_document, application_closed_switch
):
    servicer.stream_messages = [_started("Sine 1")]
    servicer.abort_status = (grpc.StatusCode.UNAVAILABLE, "Connection reset.")

    with channel_specification_document.stream_channel_data(["Sine 1"]) as stream:
        application_closed_switch.is_closed = True

        with pytest.raises(FlexLoggerError, match="application is closed"):
            list(stream)


def test___channels_with_metadata___get_channel_metadata___returns_units_range_and_rate(
    servicer, channel_specification_document
):
    servicer.channel_metadata = [_channel_metadata("Sine 1", unit="V")]

    metadata = channel_specification_document.get_channel_metadata(["Sine 1"])

    assert list(servicer.metadata_requests[0].channel_names) == ["Sine 1"]
    assert len(metadata) == 1
    assert metadata[0].channel_name == "Sine 1"
    assert metadata[0].unit == "V"
    assert metadata[0].expected_minimum == -10.0
    assert metadata[0].expected_maximum == 10.0
    assert metadata[0].actual_data_rate_hz == 1000.0
    assert metadata[0].group_path == ["Group", "Subgroup"]
    assert metadata[0].enabled
    assert not metadata[0].writable
    assert metadata[0].data_type == "double"
    assert metadata[0].errors == []
    assert metadata[0].warnings == []


def test___no_channel_names___get_channel_metadata___requests_all_channels(
    servicer, channel_specification_document
):
    servicer.channel_metadata = [_channel_metadata("Sine 1"), _channel_metadata("Sine 2")]

    metadata = channel_specification_document.get_channel_metadata()

    assert list(servicer.metadata_requests[0].channel_names) == []
    assert [channel.channel_name for channel in metadata] == ["Sine 1", "Sine 2"]


def test___server_rejects_request___get_channel_metadata___raises_flexlogger_error(
    servicer, channel_specification_document
):
    servicer.abort_status = (grpc.StatusCode.INVALID_ARGUMENT, "[-143040] Channel not found.")

    with pytest.raises(FlexLoggerError) as error_info:
        channel_specification_document.get_channel_metadata(["Missing"])

    assert error_info.value.error_code == -143040
