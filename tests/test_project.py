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
            # TODO assert on all 4 document types

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
