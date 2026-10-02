import os
import sys

from flexlogger.automation import Application

FRAME_COUNT = 10


def main(channel_names):
    """Stream live channel data from FlexLogger and print a summary of the first frames.

    Connect to an already running instance of FlexLogger with an open project. Before you connect,
    the Automation server preference must be enabled. You can enable this preference by opening the
    "File>>Preferences" menu item, and then enabling the "Automation server" preference in the
    "General" tab.
    """
    app = Application()
    project = app.get_active_project()
    if project is None:
        print("No project is open in FlexLogger!")
        return 1
    channel_specification = project.open_channel_specification_document()
    with channel_specification.stream_channel_data(
        channel_names,
        window_seconds=10.0,
        points_per_window=200,
        max_update_rate_hz=5.0,
        include_statistics=True,
        include_latest_value=True,
    ) as stream:
        for metadata in stream.metadata:
            print(
                "%s: unit %r, expected range %g to %g, %g Hz"
                % (
                    metadata.channel_name,
                    metadata.unit,
                    metadata.expected_minimum,
                    metadata.expected_maximum,
                    metadata.actual_data_rate_hz,
                )
            )
        for frame_index, frame in enumerate(stream):
            print("Frame %d (reference time %s)" % (frame.sequence_number, frame.reference_time))
            for name, channel in frame.channels.items():
                print(
                    "  %s: %d points, latest %g, window minimum %g, maximum %g, average %g"
                    % (
                        name,
                        len(channel.values),
                        channel.latest.value,
                        channel.statistics.minimum,
                        channel.statistics.maximum,
                        channel.statistics.average,
                    )
                )
            if frame_index + 1 >= FRAME_COUNT:
                # Leaving the "with" block cancels the stream.
                break
    app.disconnect()
    return 0


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) < 2:
        print("Usage: %s <name of channel> [<name of channel> ...]" % os.path.basename(__file__))
        sys.exit()
    sys.exit(main(argv[1:]))
