import os
import sys

from flexlogger.automation import Application


def main(project_path):
    """Launch FlexLogger, open a project, and gets the log file base path and name."""
    with Application.launch() as app:
        project = app.open_project(path=project_path)
        logging_specification = project.open_logging_specification_document()
        log_file_base_path = logging_specification.get_log_file_base_path()
        log_file_name = logging_specification.get_log_file_name()
        print("Log file base path: " + log_file_base_path)
        print("Log file name: " + log_file_name)
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
