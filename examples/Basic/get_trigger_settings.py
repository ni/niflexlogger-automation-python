import os
import sys

from flexlogger.automation import Application
from flexlogger.automation import StartTriggerCondition
from flexlogger.automation import StopTriggerCondition


def main(project_path):
    """Launch FlexLogger, open a project, and get the trigger settings."""
    with Application.launch() as app:
        project = app.open_project(path=project_path)
        logging_specification = project.open_logging_specification_document()

        # Get and print the start trigger settings
        start_trigger_condition, start_trigger_settings = logging_specification.get_start_trigger_settings()
        print("Start Trigger Condition: " + str(start_trigger_condition))
        if start_trigger_condition == StartTriggerCondition.CHANNEL_VALUE_CHANGE:
            print("Channel Value Change Condition :")
            print(start_trigger_settings)
        elif start_trigger_condition == StartTriggerCondition.ABSOLUTE_TIME:
            print("Start Time: " + start_trigger_settings.strftime("%x, %X"))

        # Get and print the stop trigger settings
        stop_trigger_condition, stop_trigger_settings = logging_specification.get_stop_trigger_settings()
        print("Stop Trigger Condition: " + str(stop_trigger_condition))
        if stop_trigger_condition == StopTriggerCondition.CHANNEL_VALUE_CHANGE:
            print("Channel Value Change Condition :")
            print(stop_trigger_settings)
        elif stop_trigger_condition == StopTriggerCondition.TEST_TIME_ELAPSED:
            print("Time Elapsed: " + stop_trigger_settings)

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
