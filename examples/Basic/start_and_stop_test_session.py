import os
import sys

from flexlogger.automation import Application


def main(project_path) -> int:
    """Launch FlexLogger, open a project, start and stop the test session."""
    with Application.launch() as app:
        project = app.open_project(path=project_path)
        test_session = project.test_session
        test_session.start()
        print("Test started. Press Enter to stop the test and close the project...")
        input()
        test_session.stop()
        project.close()
    return 0


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) < 2:
        print("Usage: %s <path of project to open>" % os.path.basename(__file__))
        sys.exit()
    project_path_arg = argv[1]
    sys.exit(main(project_path_arg))
