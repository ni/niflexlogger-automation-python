import sys
import time
from typing import List

from flexlogger.automation import Application


def main(argv: List[str]) -> int:
    """Connect to FlexLogger and start a test"""
    with Application.launch() as app:
        project = app.open_project(argv[0])
        temp_dir = argv[1]
        logging_specification = project.open_logging_specification_document()
        logging_specification.set_log_file_base_path(temp_dir)
        logging_specification.set_log_file_name("ShouldNotExist.tdms")
        logging_specification.set_test_property("prompts on start", "some value", True)
        project.test_session.start()
        # Make sure that if this does start running, it will actually log data
        # before we close the project.
        time.sleep(5)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
