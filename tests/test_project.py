import pytest  # type: ignore
from flexlogger import Application, FlexLoggerError

from .utils import get_project_path, open_project


class TestProject:
    @pytest.mark.integration  # type: ignore
    def test__launch_flexLogger__open_default_project__project_contains_standard_four_documents(
        self,
    ) -> None:
        with Application.launch() as app:
            with open_project(app, "DefaultProject") as project:
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

    @pytest.mark.integration  # type: ignore
    def test__launch_flexLogger__open_missing_screen__raises_exception(self) -> None:
        with Application.launch() as app:
            with open_project(app, "DefaultProject") as project:
                with pytest.raises(FlexLoggerError):
                    project.open_screen_document("Not a Screen")

    @pytest.mark.integration  # type: ignore
    def test__launch_flexlogger_and_disconnect__connect_to_existing_and_open_project__is_not_None(
        self,
    ) -> None:
        project_path = get_project_path("DefaultProject")
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
