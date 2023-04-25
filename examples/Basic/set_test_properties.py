import os
import sys

from flexlogger.automation import Application
from flexlogger.automation import TestProperty


def main(project_path):
    """Launch FlexLogger, open a project, and set test properties."""
    with Application.launch() as app:
        project = app.open_project(path=project_path)
        logging_specification = project.open_logging_specification_document()

        test_properties = []
        while True:
            name = input("Enter the name of the test property to set the value of (empty line to exit): ")
            if name == "":
                break
            value = input("Enter the test property value: ")
            prompt_on_start = input("Enter if you want to prompt on start (y/n): ") == "y"
            test_properties.append(TestProperty(name, value, prompt_on_start))

        logging_specification.set_test_properties(test_properties)
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
