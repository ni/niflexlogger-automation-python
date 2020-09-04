# import pytest  # type: ignore
from pathlib import Path

from flexlogger import Application


class TestProject:
    def test__launch_flexLogger__open_default_project__project_contains_standard_four_documents(
        self,
    ) -> None:
        project_path = Path(__file__).parent / "assets/DefaultProject/DefaultProject.flxproj"
        with Application.launch() as app:
            project = app.open_project(project_path)
            assert project is not None
            channel_specification_document = project.open_channel_specification_document()
            assert channel_specification_document is not None
            logging_specification_document = project.open_logging_specification_document()
            assert logging_specification_document is not None
            # Validate screen can be accessed with and without extension
            screen_document = project.open_screen_document("Screen")
            assert screen_document is not None
            screen_document = project.open_screen_document("Screen.flxscr")
            assert screen_document is not None
            test_specification_document = project.open_test_specification_document()
            assert test_specification_document is not None

    def test__launch_flexlogger_and_disconnect__connect_to_existing_and_open_project__is_not_None(
        self,
    ) -> None:
        project_path = Path(__file__).parent / "assets/DefaultProject/DefaultProject.flxproj"
        server_port = -1
        try:
            with Application.launch() as app:
                server_port = app.server_port
                # This should prevent FlexLogger from closing when app goes out of scope
                app.disconnect()
            with Application(server_port=server_port) as app:
                project = app.open_project(project_path)
                assert project is not None
        finally:
            if server_port != -1:
                Application(server_port=server_port).close()
