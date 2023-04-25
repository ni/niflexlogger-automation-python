import os
import sys

from flexlogger.automation import Application
from flexlogger.automation import DataRateLevel


DATA_RATE_LEVEL_LOOKUP = {
    "Slow": DataRateLevel.SLOW,
    "Medium": DataRateLevel.MEDIUM,
    "Fast": DataRateLevel.FAST
}


def main(project_path):
    """Launch FlexLogger, open a project, and set the data rate values."""
    with Application.launch() as app:
        project = app.open_project(path=project_path)
        channel_specification = project.open_channel_specification_document()
        slow_date_rate = input("Specify the data rate value for the Slow level in Hertz: ")
        channel_specification.set_data_rate(DataRateLevel.SLOW, float(slow_date_rate))
        medium_date_rate = input("Specify the data rate value for the Medium level in Hertz: ")
        channel_specification.set_data_rate(DataRateLevel.MEDIUM, float(medium_date_rate))
        fast_date_rate = input("Specify the data rate value for the Fast level in Hertz: ")
        channel_specification.set_data_rate(DataRateLevel.FAST, float(fast_date_rate))
        channel_name = input("Enter the name of the channel you want to set the data rate level of: ")
        data_rate_level = input("Enter the data rate level you want to set (Slow, Medium or Fast: ")
        channel_specification.set_data_rate_level(channel_name, DATA_RATE_LEVEL_LOOKUP.get(data_rate_level))

        print("Data rate set. Press Enter to save and close the project...")
        input()
        project.close()
    return 0


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) < 2:
        print("Usage: %s <path of project to open>" % os.path.basename(__file__))
        sys.exit()
    project_path_arg = argv[1]
    sys.exit(main(project_path_arg))
