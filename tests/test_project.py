from shutil import rmtree
from time import sleep
from pathlib import Path

import pytest  # type: ignore
from flexlogger.automation import Application, FlexLoggerError

from .utils import (
    assert_no_flexloggers_running,
    copy_project,
    get_project_path,
    kill_all_open_flexloggers,
    open_project,
)


class TestProject:
    @pytest.mark.integration  # type: ignore
    def test__launch_flexLogger__open_default_project__project_contains_standard_four_documents(
        self, app: Application
    ) -> None:
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
    def test__launch_flexLogger__open_missing_screen__raises_exception(
        self, app: Application
    ) -> None:
        with open_project(app, "DefaultProject") as project:
            with pytest.raises(FlexLoggerError):
                project.open_screen_document("Not a Screen")

    # This test can hang if the API doesn't handle this error correctly, so set a
    # timeout
    @pytest.mark.timeout(120)  # type: ignore
    @pytest.mark.integration  # type: ignore
    def test__remove_channel_specification_file__open_project__raises_exception(
        self, app: Application
    ) -> None:
        with copy_project("DefaultProject") as project_path:
            cache_dir = project_path.parent / ".cache"
            if cache_dir.exists():
                rmtree(str(cache_dir))
            (project_path.parent / "Channel Specification.flxio").unlink()
            project = None
            try:
                with pytest.raises(FlexLoggerError):
                    project = app.open_project(project_path)
            finally:
                if project is not None:
                    project.close()

    @pytest.mark.integration  # type: ignore
    def test__launch_flexlogger_and_disconnect__connect_to_existing_and_open_project__is_not_None(
        self,
    ) -> None:
        kill_all_open_flexloggers()
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

    @pytest.mark.integration  # type: ignore
    def test__open_project__open_different_project__using_original_project_raises_exception(
        self,
    ) -> None:
        kill_all_open_flexloggers()
        project_path = get_project_path("DefaultProject")
        second_project_path = get_project_path("ProjectWithTestProperties")
        with Application.launch() as app:
            first_project = app.open_project(project_path)
            app.open_project(second_project_path)
            with pytest.raises(FlexLoggerError):
                first_project.open_channel_specification_document()

    @pytest.mark.integration  # type: ignore
    def test__open_project_that_does_not_exist__raises_exception(self) -> None:
        kill_all_open_flexloggers()
        project_path = get_project_path("DoesNotExist")
        with Application.launch() as app:
            with pytest.raises(FlexLoggerError):
                app.open_project(project_path)

    @pytest.mark.integration  # type: ignore
    def test__open_project__close_project__using_original_project_raises_exception(self) -> None:
        kill_all_open_flexloggers()
        project_path = get_project_path("DefaultProject")
        with Application.launch() as app:
            first_project = app.open_project(project_path)
            first_project.close()
            with pytest.raises(FlexLoggerError):
                first_project.open_channel_specification_document()

    @pytest.mark.integration  # type: ignore
    def test__launch_application__close_application__using_application_raises_exception(
        self,
    ) -> None:
        kill_all_open_flexloggers()
        app = Application.launch()
        app.close()
        with pytest.raises(FlexLoggerError):
            app.open_project(get_project_path("DefaultProject"))

    @pytest.mark.integration  # type: ignore
    def test__disconnect_application__using_application_raises_exception(self) -> None:
        kill_all_open_flexloggers()
        original_app = Application.launch()
        try:
            new_app = Application(server_port=original_app.server_port)
            new_app.disconnect()
            with pytest.raises(FlexLoggerError):
                new_app.open_project(get_project_path("DefaultProject"))
        finally:
            original_app.close()

    @pytest.mark.integration  # type: ignore
    def test__open_project__close_application__using_project_raises_exception(self) -> None:
        kill_all_open_flexloggers()
        app = Application.launch()
        project = app.open_project(get_project_path("DefaultProject"))
        app.close()
        with pytest.raises(FlexLoggerError):
            project.open_channel_specification_document()

    @pytest.mark.integration  # type: ignore
    def test__launch_application__launch_application_again__raises_exception(self) -> None:
        kill_all_open_flexloggers()
        with Application.launch():
            # We expect this to fail because we don't support multiple instances of FlexLogger
            # running at the same time.
            new_app = None
            try:
                with pytest.raises(RuntimeError):
                    new_app = Application.launch(timeout=20)
            finally:
                # if the test fails, try not to mess up future tests
                if new_app is not None:
                    new_app.close()

    @pytest.mark.integration  # type: ignore
    def test__launch_application__close_application__application_has_closed(self) -> None:
        kill_all_open_flexloggers()

        with Application.launch() as app:
            # Opening a project will make closing the application take longer
            app.open_project(get_project_path("DefaultProject"))

        assert_no_flexloggers_running()

    @pytest.mark.integration  # type: ignore
    def test__connect_to_application__close_application__application_has_closed(self) -> None:
        kill_all_open_flexloggers()
        app = Application.launch()
        # Opening a project will make closing the application take longer
        app.open_project(get_project_path("DefaultProject"))

        app2 = Application(app.server_port)
        app2.close()

        assert_no_flexloggers_running()

    @pytest.mark.integration  # type: ignore
    def test__launch_application__active_project_is_none(self) -> None:
        kill_all_open_flexloggers()
        with Application.launch() as app:
            active_project = app.get_active_project()
            assert active_project is None

    @pytest.mark.integration  # type: ignore
    def test__launch_application__open_and_close_project__active_project_is_none(self) -> None:
        kill_all_open_flexloggers()
        with Application.launch() as app:
            project = app.open_project(get_project_path("DefaultProject"))
            project.close()
            active_project = app.get_active_project()
            assert active_project is None

    @pytest.mark.integration  # type: ignore
    def test__launch_application__open_project__active_project_matches_open_project(self) -> None:
        kill_all_open_flexloggers()
        with Application.launch() as app:
            project = app.open_project(get_project_path("DefaultProject"))
            active_project = app.get_active_project()
            assert active_project is not None
            assert project._identifier == active_project._identifier

    # This test can hang if the server port file never gets created, so set a
    # timeout
    @pytest.mark.timeout(120)  # type: ignore
    @pytest.mark.integration  # type: ignore
    def test__launch_flexlogger_separately__connect_to_existing_and_close__application_has_closed(
        self,
    ) -> None:
        kill_all_open_flexloggers()
        # Launch the way that Application.launch() does, but don't connect
        real_server_port = Application._launch_flexlogger(60)
        # The port file doesn't get written out until slightly after the mapped file
        # that _launch_flexlogger() is waiting for.
        # So wait for the file to exist before proceeding with the test.
        server_port_file_path = Application._get_server_port_file_path()
        while not server_port_file_path.exists():
            sleep(1)

        app = Application()
        assert real_server_port == app.server_port
        app.close()

        assert_no_flexloggers_running()

    # This test can hang if the application pops a "save changes" dialog box, so set a
    # timeout
    @pytest.mark.timeout(120)  # type: ignore
    @pytest.mark.integration  # type: ignore
    def test__make_change_to_project__close_application__no_save_dialog_box(self) -> None:
        kill_all_open_flexloggers()
        with copy_project("ProjectWithProducedData") as new_project_path:
            with Application.launch() as app:
                project = app.open_project(new_project_path)
                logging_specification = project.open_logging_specification_document()
                logging_specification.set_log_file_name("SomeNewName")
        # Just verify that closing the app doesn't prompt to save the project (this test
        # will timeout if it does)

    @pytest.mark.integration
    def test__open_project__active_project_path_matches_loaded_path(self) -> None:
        with copy_project("DefaultProject") as new_project_path:
            with Application.launch() as app:
                project = app.open_project(new_project_path)
                assert project.project_file_path == new_project_path
