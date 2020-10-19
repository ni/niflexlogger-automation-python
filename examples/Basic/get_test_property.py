import os
import sys

from flexlogger.automation import Application


def main(project_path) -> int:
    """Launch FlexLogger, open a project, and gets the value of a test property."""
    with Application.launch() as app:
        project = app.open_project(path=project_path)
        test_property_name = input("Enter the name of the test property to get the value of: ")
        logging_specification = project.open_logging_specification_document()
        test_property = logging_specification.get_test_property(test_property_name)
        print("Test property:")
        print(test_property)
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
