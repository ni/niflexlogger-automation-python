import os
import sys

from flexlogger.automation import Application
from flexlogger.automation import ValueChangeCondition
from flexlogger.automation import ValueChangeType


def main(project_path):
    """Launch FlexLogger, open a project, and set the trigger settings."""
    with Application.launch() as app:
        project = app.open_project(path=project_path)
        logging_specification = project.open_logging_specification_document()

        start_value_change_condition = ValueChangeCondition()
        start_value_change_condition.value_change_type = ValueChangeType.ENTER_RANGE
        start_value_change_condition.channel_name = 'Replace this string with the channel name to monitor.'
        start_value_change_condition.min_value = 1.0
        start_value_change_condition.max_value = 2.0
        start_value_change_condition.time = 0.0

        stop_value_change_condition = ValueChangeCondition()
        stop_value_change_condition.value_change_type = ValueChangeType.FALL_BELOW_VALUE
        stop_value_change_condition.channel_name = 'Replace this string with the channel name to monitor.'
        stop_value_change_condition.threshold = 1.0
        stop_value_change_condition.time = 0.0

        logging_specification.set_start_trigger_settings_to_value_change(start_value_change_condition)
        logging_specification.set_stop_trigger_settings_to_value_change(stop_value_change_condition)

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
