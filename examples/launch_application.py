import os
import sys

from flexlogger import Application

if len(sys.argv) < 2:
    print("Usage: %s <path of project to open>" % os.path.basename(__file__))
    sys.exit(1)

project_path = sys.argv[1]
with Application() as a:
    project = a.open_project(path=project_path)
    print("Press Enter to close project...")
    input()
    project.close(allow_prompts=False)
