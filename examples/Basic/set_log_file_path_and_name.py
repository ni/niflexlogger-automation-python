import os
import sys

from flexlogger.automation import Application


def main(project_path) -> int:
    """Launch FlexLogger, open a project, and sets the log file base path and name."""
    with Application.launch() as app:
        project = app.open_project(path=project_path)
        log_file_base_path = input("Enter the log file base path: ")
        log_file_name = input("Enter the log file name: ")
        logging_specification = project.open_logging_specification_document()
        logging_specification.set_log_file_base_path(log_file_base_path)
        logging_specification.set_log_file_name(log_file_name)
        print("Log file base path and name set. Press Enter to close the project...")
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
