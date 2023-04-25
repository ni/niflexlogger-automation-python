import os
import sys

from flexlogger.automation import Application


def main(project_path):
    """Launch FlexLogger, open a project, and set the log file description."""
    with Application.launch() as app:
        project = app.open_project(path=project_path)
        log_file_description = input("Enter the log file description: ")
        logging_specification = project.open_logging_specification_document()
        logging_specification.set_log_file_description(log_file_description)
        print("Log file description set. Press Enter to close the project...")
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
