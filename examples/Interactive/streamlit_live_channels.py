"""Show live FlexLogger channel data in a Streamlit app.

The overview page lists the channels of the open project with their unit, data rate, and current
value. Select a channel to see its live graph, which shows the same peak-preserving view of the last
few seconds as the FlexLogger high speed graph. Zoom into the graph (mouse wheel or drag) to pause
the window and inspect data points; double-click the graph to zoom out and resume the live view.

Connect to an already running instance of FlexLogger with an open project. Before you connect, the
Automation server preference must be enabled. You can enable this preference by opening the
"File>>Preferences" menu item, and then enabling the "Automation server" preference in the
"General" tab.

Requires Streamlit 1.37 or later. Run with:

    streamlit run streamlit_live_channels.py
"""

import math
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field

import altair as alt
import pandas as pd
import streamlit as st
from flexlogger.automation import Application, FlexLoggerError
from streamlit import config

WINDOW_SECONDS = 10.0
POINTS_PER_WINDOW = 800
UPDATE_RATE_HZ = 10.0
MAX_OPEN_STREAMS = 4
OVERVIEW_REFRESH_SECONDS = 0.2
OVERVIEW_POLL_PAUSE_SECONDS = 0.1
MAX_RATE_MEASURE_CHANNELS = 64
RATE_MEASURE_TIMEOUT_SECONDS = 5.0
RATE_MEASURE_RETRY_SECONDS = 30.0
ZOOM_SELECTION = "zoom"

# Streamlit sends a chart that is 10 KB or larger as a reference to a cached copy when it repeats.
# With a chart that changes ten times per second the browser can lose that copy, which fails with
# "Cached ForwardMsg MISS" and stops the live updates. Sending every message in full avoids that.
config.set_option("global.minCachedMessageSize", 1e12)


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


@st.cache_resource(show_spinner=False)
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


@dataclass
class OverviewSnapshot:
    """What the overview page shows, read from FlexLogger in one pass."""

    project_name: str = ""
    session_state: str = ""
    channels: list = field(default_factory=list)
    values: list = field(default_factory=list)
    error: str = ""


def read_overview():
    project = get_application().get_active_project()
    if project is None:
        return OverviewSnapshot(error="Open a project in FlexLogger.")

    project_path = project.project_file_path
    channel_specification = project.open_channel_specification_document()
    # Only acquired channels with a floating point value can be streamed; variables are writable and not streamed.
    channels = [
        channel
        for channel in channel_specification.get_channel_metadata()
        if channel.data_type == "double" and not channel.writable
    ]
    return OverviewSnapshot(
        project_name=project_path.stem if project_path else "Unsaved project",
        session_state=project.test_session.state.name,
        channels=channels,
        values=[get_current_value(channel_specification, channel.channel_name) for channel in channels],
    )


class OverviewPoller:
    """Read the overview data from FlexLogger on a background thread.

    Each automation call can take half a second or more. Reading in the page's refresh fragment made a
    refresh interval shorter than that pile up reruns, which stalled the app and swallowed table clicks.
    The fragment now only copies the latest snapshot, so it can refresh as fast as it likes.
    """

    def __init__(self):
        self._snapshot = None
        self._measured_rates_hz = {}
        self._last_measure_attempt = {}
        self._lock = threading.Lock()
        self._stopped = threading.Event()
        threading.Thread(target=self._run, name="overview-poller", daemon=True).start()

    @property
    def snapshot(self):
        with self._lock:
            return self._snapshot

    def rate_hz(self, metadata):
        """Return the channel's data rate, measured from its samples when FlexLogger reports none."""
        if metadata.actual_data_rate_hz > 0:
            return metadata.actual_data_rate_hz
        with self._lock:
            return self._measured_rates_hz.get(metadata.channel_name, 0.0)

    def stop(self):
        self._stopped.set()

    def _run(self):
        while not self._stopped.is_set():
            try:
                snapshot = read_overview()
            except (FlexLoggerError, RuntimeError) as error:
                # RuntimeError means no FlexLogger with an enabled automation server was found.
                snapshot = OverviewSnapshot(error=str(error))
                # Detect the server port again, because FlexLogger may have restarted on another port.
                get_application.clear()
            else:
                try:
                    self._measure_missing_rates(snapshot.channels)
                except FlexLoggerError:
                    # The rate stays unknown and is measured again after the retry interval.
                    pass
            with self._lock:
                self._snapshot = snapshot
            # Avoids a busy loop when FlexLogger answers immediately, for example with no project open.
            self._stopped.wait(OVERVIEW_POLL_PAUSE_SECONDS)

    def _measure_missing_rates(self, channels):
        # Channels without hardware timing, such as calculated channels, report a data rate of 0 even
        # though they produce samples. The sample interval of their raw stream gives the rate.
        now = time.monotonic()
        names = []
        for channel in channels:
            name = channel.channel_name
            if self.rate_hz(channel) > 0:
                continue
            if now - self._last_measure_attempt.get(name, -RATE_MEASURE_RETRY_SECONDS) < RATE_MEASURE_RETRY_SECONDS:
                continue
            self._last_measure_attempt[name] = now
            names.append(name)
        names = names[:MAX_RATE_MEASURE_CHANNELS]
        if not names:
            return

        channel_specification = get_application().get_active_project().open_channel_specification_document()
        pending = set(names)
        with channel_specification.stream_raw_channel_data(names) as stream:
            stream.start_background()
            deadline = time.monotonic() + RATE_MEASURE_TIMEOUT_SECONDS
            while pending and time.monotonic() < deadline and not self._stopped.is_set():
                frame = stream.latest_frame
                for name, samples in (frame.channels.items() if frame else []):
                    intervals = [s.sample_interval_seconds for s in samples.segments if s.sample_interval_seconds]
                    if name in pending and intervals:
                        with self._lock:
                            self._measured_rates_hz[name] = 1.0 / intervals[0]
                        pending.discard(name)
                time.sleep(0.05)


@st.cache_resource
def get_overview_poller():
    return OverviewPoller()


def overview_page():
    st.title("FlexLogger project")
    overview_table()


@st.fragment(run_every=OVERVIEW_REFRESH_SECONDS)
def overview_table():
    poller = get_overview_poller()
    snapshot = poller.snapshot
    if snapshot is None:
        st.info("Connecting to FlexLogger...")
        return
    if snapshot.error:
        st.warning(snapshot.error)
        return

    st.caption("%s - test session: %s" % (snapshot.project_name, snapshot.session_state))
    metadata = snapshot.channels
    names = [channel.channel_name for channel in metadata]
    table = pd.DataFrame(
        {
            "Channel": names,
            "Value": snapshot.values,
            "Unit": [channel.unit for channel in metadata],
            "Rate (Hz)": [format_rate(poller.rate_hz(channel)) for channel in metadata],
        }
    )
    # A fixed key keeps the selection when the live values in the table change between reruns; a new
    # key per visit makes the table come back unselected instead of reopening the last channel.
    table_key = "channels_%d" % st.session_state.get("table_version", 0)
    selection = st.dataframe(
        table, key=table_key, hide_index=True, on_select="rerun", selection_mode="single-row"
    )
    if selection.selection.rows:
        # One page and a full rerun: st.switch_page races in-flight table refreshes over slow links.
        st.query_params["channel"] = names[selection.selection.rows[0]]
        st.session_state["table_version"] = st.session_state.get("table_version", 0) + 1
        st.rerun(scope="app")


def format_rate(rate_hz):
    return "%g" % rate_hz if rate_hz > 0 else "-"


def format_range(metadata):
    # A channel without a configured range reports infinite limits.
    if math.isfinite(metadata.expected_minimum) and math.isfinite(metadata.expected_maximum):
        return "%g to %g" % (metadata.expected_minimum, metadata.expected_maximum)
    return "not specified"


def channel_page(channel_name):
    if st.button("← All channels"):
        del st.query_params["channel"]
        st.rerun()
    project = get_application().get_active_project()
    if project is None:
        st.warning("Open a project in FlexLogger.")
        return

    project_key = str(project.project_file_path)
    channel_specification = get_channel_streams(project_key).channel_specification
    try:
        metadata = channel_specification.get_channel_metadata([channel_name])[0]
    except FlexLoggerError:
        st.warning("The project has no channel named %s." % channel_name)
        return
    st.title(channel_name)
    # Streamlit offers no option to remove single toolbar buttons from a chart, so hide the PNG download.
    st.html(
        '<style>.stTooltipHoverTarget:has(> button[aria-label="Download as PNG"]) { display: none !important; }</style>'
    )
    st.caption(
        "Unit: %s - Range: %s - Rate: %s Hz - Group: %s"
        % (
            metadata.unit or "none",
            format_range(metadata),
            format_rate(get_overview_poller().rate_hz(metadata)),
            " / ".join(metadata.group_path),
        )
    )
    live_view(channel_name, project_key, metadata.unit)


def make_chart(channel_name, unit, times, values, key):
    # Plotting the minimum and maximum points as one line keeps every peak, like FlexLogger does.
    data = pd.DataFrame({"time": times, "value": values})
    zoom = alt.selection_interval(bind="scales", name=ZOOM_SELECTION)
    chart = (
        alt.Chart(data)
        .mark_line()
        .encode(
            x=alt.X("time:Q", title="Time (s)"),
            y=alt.Y(
                "value:Q",
                title="%s (%s)" % (channel_name, unit) if unit else channel_name,
                scale=alt.Scale(zero=False),
            ),
        )
        .add_params(zoom)
    )
    return st.altair_chart(chart, key=key, on_select="rerun")


@st.fragment(run_every=1.0 / UPDATE_RATE_HZ)
def live_view(channel_name, project_key, unit):
    channel_streams = get_channel_streams(project_key)
    try:
        latest_frame = channel_streams.get(channel_name).latest_frame
    except FlexLoggerError as error:
        st.error(str(error))
        if st.button("Reconnect"):
            channel_streams.close()
            get_overview_poller().stop()
            st.cache_resource.clear()
            st.rerun()
        return

    # Changing the key creates a fresh chart, which is how the Resume button clears a zoom.
    version = st.session_state.get("chart_version", 0)
    chart_key = "chart_%s_%d" % (channel_name, version)
    shown_key = "shown_frame_" + channel_name
    # Zooming in or panning the graph sets the selection; zooming all the way out clears it.
    chart_state = st.session_state.get(chart_key)
    zoomed = bool(chart_state and chart_state.selection.get(ZOOM_SELECTION))
    # While the graph is zoomed, keep showing the frame the user zoomed into so the points hold still.
    frame = st.session_state.get(shown_key) if zoomed else latest_frame
    if frame is None:
        st.info("Waiting for data...")
        return
    st.session_state[shown_key] = frame

    channel = frame.channels[channel_name]
    # A channel without a published value yet has no latest value.
    current_value = "%.4g %s" % (channel.latest.value, unit) if channel.latest else "n/a"
    left, middle, right = st.columns(3)
    left.metric("Current value", current_value)
    middle.metric("Window minimum", "%.4g" % channel.statistics.minimum)
    right.metric("Window maximum", "%.4g" % channel.statistics.maximum)
    # The status row sits above the graph and keeps its height so the graph does not move when it changes.
    status, resume = st.columns([3, 1], vertical_alignment="center")
    if zoomed:
        status.warning("Paused: the graph is zoomed. Double-click it to zoom out and resume.")
        if resume.button("Resume live view"):
            st.session_state["chart_version"] = version + 1
            st.rerun(scope="fragment")
    else:
        resume.empty()
        status.success(
            "Live - frame %d, skipped frames: %d. Zooming the graph pauses it."
            % (frame.sequence_number, frame.dropped_frames_total)
        )
    make_chart(channel_name, unit, channel.times_seconds, channel.values, chart_key)


st.set_page_config(page_title="FlexLogger live channels")
selected_channel = st.query_params.get("channel")
if selected_channel:
    channel_page(selected_channel)
else:
    overview_page()
