import os
import sys

from flexlogger.automation import Application, LogFileType


def main(project_path):
    """Launch FlexLogger, open a project, run a test session, and show log file."""
    with Application.launch() as app:
        project = app.open_project(path=project_path)
        logging_specification = project.open_logging_specification_document()
        logging_specification.remove_log_files(delete_files=True)
        test_session = project.test_session
        test_session.start()
        print("Test started. Press Enter to stop the test and close the project...")
        input()
        test_session.stop()
        log_files = logging_specification.get_log_files(LogFileType.TDMS)
        project.close()
        print("The following TDMS log files were created during the test session:")
        for log_file in log_files:
            print(log_file)
    return 0


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) < 2:
        print("Usage: %s <path of project to open>" % os.path.basename(__file__))
        sys.exit()
    project_path_arg = argv[1]
    sys.exit(main(project_path_arg))
