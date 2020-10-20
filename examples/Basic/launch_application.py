import os
import sys

from flexlogger.automation import Application


def main(project_path) -> int:
    """Launch FlexLogger and open a project."""
    with Application.launch() as app:
        project = app.open_project(path=project_path)
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
