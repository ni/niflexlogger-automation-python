import os
import sys

from flexlogger.automation import Application


def main(project_path):
    """Launch FlexLogger, open a project, and get the value of a channel."""
    with Application.launch() as app:
        project = app.open_project(path=project_path)
        channel_name = input("Enter the name of the channel to get the value of: ")
        channel_specification = project.open_channel_specification_document()
        channel_value = channel_specification.get_channel_value(channel_name)
        print("Channel value:")
        print(channel_value)
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
