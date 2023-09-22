import os
import sys

from flexlogger.automation import Application


def main(project_path):
    """Launch FlexLogger and open a project."""
    # Note that using the "with" statement here means that when the block
    # goes out of scope, the application will be closed.  To prevent this,
    # call app.disconnect() before the scope ends.
    with Application.launch() as app:
        project = app.open_project(path=project_path, timeout=180)
        print("Press Enter to close project...")
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
