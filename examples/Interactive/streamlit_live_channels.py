"""Show live FlexLogger channel data in a Streamlit app.

The overview page lists the channels of the open project with their unit, data rate, and current
value. Select a channel to see its live graph, which shows the same peak-preserving view of the last
few seconds as the FlexLogger high speed graph.

Connect to an already running instance of FlexLogger with an open project. Before you connect, the
Automation server preference must be enabled. You can enable this preference by opening the
"File>>Preferences" menu item, and then enabling the "Automation server" preference in the
"General" tab.

Requires Streamlit 1.37 or later. Run with:

    streamlit run streamlit_live_channels.py
"""

import threading
from collections import OrderedDict

import pandas as pd
import streamlit as st
from flexlogger.automation import Application, FlexLoggerError

WINDOW_SECONDS = 10.0
POINTS_PER_WINDOW = 800
UPDATE_RATE_HZ = 10.0
MAX_OPEN_STREAMS = 4


class ChannelStreams:
    """Keep a few channel streams open and cancel the least recently used one.

    Streamlit never tells a cached resource that it was evicted, so the streams are cancelled here.
    FlexLogger limits how many streams can be open at the same time.
    """

    def __init__(self, channel_specification):
        self.channel_specification = channel_specification
        self._streams = OrderedDict()
        self._lock = threading.Lock()

    def get(self, channel_name):
        with self._lock:
            stream = self._streams.pop(channel_name, None)
            if stream is None:
                stream = self.channel_specification.stream_channel_data(
                    [channel_name],
                    window_seconds=WINDOW_SECONDS,
                    points_per_window=POINTS_PER_WINDOW,
                    max_update_rate_hz=UPDATE_RATE_HZ,
                    include_statistics=True,
                    include_latest_value=True,
                )
                # Receive frames on a worker thread so the app can read stream.latest_frame.
                stream.start_background()
            self._streams[channel_name] = stream
            while len(self._streams) > MAX_OPEN_STREAMS:
                _, least_recently_used_stream = self._streams.popitem(last=False)
                least_recently_used_stream.cancel()
            return stream

    def close(self):
        with self._lock:
            for stream in self._streams.values():
                stream.cancel()
            self._streams.clear()


@st.cache_resource
def get_application():
    return Application()


# Cached resources are shared by every browser session. The project path is the cache key, so
# opening a different project in FlexLogger starts a new set of streams.
@st.cache_resource
def get_channel_streams(project_key):
    project = get_application().get_active_project()
    return ChannelStreams(project.open_channel_specification_document())


def get_current_value(channel_specification, channel_name):
    try:
        return channel_specification.get_channel_value(channel_name).value
    except FlexLoggerError:
        # A channel that is not available, configured or enabled has no value.
        return None


def overview_page():
    st.title("FlexLogger project")
    project = get_application().get_active_project()
    if project is None:
        st.warning("Open a project in FlexLogger.")
        return

    project_path = project.project_file_path
    project_name = project_path.stem if project_path else "Unsaved project"
    st.caption("%s - test session: %s" % (project_name, project.test_session.state.name))
    channel_specification = project.open_channel_specification_document()
    # Only channels with a floating point value can be streamed.
    metadata = [
        channel
        for channel in channel_specification.get_channel_metadata()
        if channel.data_type == "double"
    ]
    names = [channel.channel_name for channel in metadata]
    table = pd.DataFrame(
        {
            "Channel": names,
            "Value": [get_current_value(channel_specification, name) for name in names],
            "Unit": [channel.unit for channel in metadata],
            "Rate (Hz)": [channel.actual_data_rate_hz for channel in metadata],
        }
    )
    selection = st.dataframe(table, hide_index=True, on_select="rerun", selection_mode="single-row")
    if selection.selection.rows:
        st.session_state["channel"] = names[selection.selection.rows[0]]
        st.switch_page(channel_page_ref)


def channel_page():
    channel_name = st.session_state.get("channel")
    if not channel_name:
        st.switch_page(overview_page_ref)
    project = get_application().get_active_project()
    if project is None:
        st.warning("Open a project in FlexLogger.")
        return

    project_key = str(project.project_file_path)
    channel_specification = get_channel_streams(project_key).channel_specification
    metadata = channel_specification.get_channel_metadata([channel_name])[0]
    st.title(channel_name)
    st.caption(
        "Unit: %s - Range: %g to %g - Rate: %g Hz - Group: %s"
        % (
            metadata.unit or "none",
            metadata.expected_minimum,
            metadata.expected_maximum,
            metadata.actual_data_rate_hz,
            " / ".join(metadata.group_path),
        )
    )
    live_view(channel_name, project_key, metadata.unit)


@st.fragment(run_every=1.0 / UPDATE_RATE_HZ)
def live_view(channel_name, project_key, unit):
    channel_streams = get_channel_streams(project_key)
    try:
        frame = channel_streams.get(channel_name).latest_frame
    except FlexLoggerError as error:
        st.error(str(error))
        if st.button("Reconnect"):
            channel_streams.close()
            st.cache_resource.clear()
            st.rerun()
        return
    if frame is None:
        st.info("Waiting for data...")
        return

    channel = frame.channels[channel_name]
    left, middle, right = st.columns(3)
    left.metric("Current value", "%.4g %s" % (channel.latest.value, unit))
    middle.metric("Window minimum", "%.4g" % channel.statistics.minimum)
    right.metric("Window maximum", "%.4g" % channel.statistics.maximum)
    # Plotting the minimum and maximum points as one line keeps every peak, like FlexLogger does.
    chart = pd.DataFrame({"Time (s)": channel.times_seconds, channel_name: channel.values})
    st.line_chart(chart, x="Time (s)", y=channel_name)
    st.caption(
        "Frame %d - skipped frames: %d" % (frame.sequence_number, frame.dropped_frames_total)
    )


overview_page_ref = st.Page(overview_page, title="Project", default=True)
channel_page_ref = st.Page(channel_page, title="Channel", url_path="channel")
st.navigation([overview_page_ref, channel_page_ref]).run()
