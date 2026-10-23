import argparse
import csv
import sys
import threading
import time
from datetime import timedelta

from flexlogger.automation import Application

DEFAULT_SECONDS = 10.0


def main(channel_names, seconds, csv_path):
    """Stream every sample of channels from FlexLogger for a while and check that none is missing.

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
    sample_counts = dict((name, 0) for name in channel_names)
    gap_count = 0
    csv_file = open(csv_path, "w", newline="") if csv_path else None
    try:
        csv_writer = csv.writer(csv_file) if csv_file else None
        if csv_writer:
            csv_writer.writerow(["Channel", "Time (UTC)", "Value"])
        with channel_specification.stream_raw_channel_data(
            channel_names, max_update_rate_hz=10.0
        ) as stream:
            rates = dict(
                (metadata.channel_name, metadata.actual_data_rate_hz)
                for metadata in stream.metadata
            )
            print("Streaming %s for %g seconds..." % (", ".join(channel_names), seconds))
            # Cancelling the stream from a timer ends the loop below without an error.
            timer = threading.Timer(seconds, stream.cancel)
            timer.daemon = True
            start_time = time.monotonic()
            timer.start()
            for frame in stream:
                for name, channel in frame.channels.items():
                    sample_counts[name] += len(channel)
                    for segment in channel.segments:
                        if segment.follows_gap:
                            gap_count += 1
                            gap_time = frame.reference_time + timedelta(
                                seconds=segment.start_offset_seconds
                            )
                            print("  %s: samples are missing before %s" % (name, gap_time))
                    if csv_writer:
                        for timestamp, value in zip(channel.timestamps(), channel.values):
                            csv_writer.writerow([name, timestamp.isoformat(), value])
            elapsed_seconds = time.monotonic() - start_time
            timer.cancel()
    finally:
        if csv_file:
            csv_file.close()

    print("Received samples in %.1f seconds:" % elapsed_seconds)
    for name in channel_names:
        print(
            "  %s: %d samples, about %d expected at %g Hz"
            % (name, sample_counts[name], rates[name] * elapsed_seconds, rates[name])
        )
    print("Segments after missing samples: %d" % gap_count)
    if csv_path:
        print("Samples written to %s" % csv_path)
    app.disconnect()
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Stream every sample of FlexLogger channels and check that none is missing."
    )
    parser.add_argument("channel_names", nargs="+", metavar="channel", help="a channel to stream")
    parser.add_argument(
        "--seconds",
        type=float,
        default=DEFAULT_SECONDS,
        help="how long to stream, in seconds (default: %g)" % DEFAULT_SECONDS,
    )
    parser.add_argument("--csv", metavar="path", help="write every sample to this CSV file")
    arguments = parser.parse_args()
    sys.exit(main(arguments.channel_names, arguments.seconds, arguments.csv))
