import os
import sys

from datetime import datetime
from datetime import timedelta
from flexlogger.automation import Application


def main(project_path):
    """Launch FlexLogger, open a project, and set the trigger settings."""
    with Application.launch() as app:
        project = app.open_project(path=project_path)
        logging_specification = project.open_logging_specification_document()

        # Set the start trigger settings.
        # test_start_time is treated as UTC unless a timezone is explicitly specified
        test_start_time = datetime.utcnow()
        logging_specification.set_start_trigger_settings_to_absolute_time(test_start_time)
        # Set the stop trigger settings
        duration = timedelta(seconds=100)
        logging_specification.set_stop_trigger_settings_to_duration(duration)

        print("Press Enter to close the project...")
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
