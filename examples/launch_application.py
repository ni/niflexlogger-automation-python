import os
import sys
from typing import List

from flexlogger.automation import Application


def main(argv: List[str] = None) -> int:
    """Launch FlexLogger and open a project."""
    if argv is None:
        argv = sys.argv
    if len(argv) < 2:
        print("Usage: %s <path of project to open>" % os.path.basename(__file__))
        return 1

    project_path = argv[1]
    with Application.launch() as app:
        project = app.open_project(path=project_path)
        print("Press Enter to close project...")
        input()
        project.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
