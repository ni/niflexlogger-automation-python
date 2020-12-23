import os
import subprocess
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator

import pytest  # type: ignore
from flexlogger.automation import (
    Application,
    FlexLoggerError,
    Project,
    TestSessionState,
)
from nptdms import TdmsFile  # type: ignore

from .utils import (
    copy_project,
    get_project_path,
    kill_all_open_flexloggers,
    open_project,
)


@pytest.fixture(scope="class")
def project_with_produced_data(app: Application) -> Iterator[Project]:
    """Fixture for opening ProjectWithProducedData.

    This is useful to improve test time by not opening/closing this project in every test.
    """
    with copy_project("ProjectWithProducedData") as project_path:
        project = app.open_project(project_path)
        yield project
        try:
            project.close()
        except FlexLoggerError:
            # utils.kill_all_open_flexloggers may have killed this process already, that's fine
            pass


class TestTestSession:
    @pytest.mark.integration  # type: ignore
    @pytest.mark.parametrize(
        "project_name,expected_state",
        [
            ("DefaultProject", TestSessionState.NO_VALID_LOGGED_CHANNELS),
            ("ProjectWithError", TestSessionState.INVALID_CONFIGURATION),
            ("ProjectWithProducedData", TestSessionState.IDLE),
        ],
    )  # type: ignore
    def test__open_project__get_test_session_state__state_matches_project(
        self, project_name: str, expected_state: TestSessionState, app: Application
    ) -> None:
        with open_project(app, project_name) as project:
            assert expected_state == project.test_session.state

    @pytest.mark.integration  # type: ignore
    @pytest.mark.parametrize(
        "project_name", [("DefaultProject"), ("ProjectWithError")]
    )  # type: ignore
    def test__open_project_that_cannot_be_started__start_test_session__exception_raised(
        self, project_name: str, app: Application
    ) -> None:
        with open_project(app, project_name) as project:
            with pytest.raises(FlexLoggerError):
                project.test_session.start()

    @pytest.mark.integration  # type: ignore
    def test__open_valid_project__start_test_session__test_session_started(
        self, app: Application, project_with_produced_data: Project
    ) -> None:
        project = project_with_produced_data
        test_session_started = project.test_session.start()
        try:
            assert test_session_started is True
            assert TestSessionState.RUNNING == project.test_session.state
        finally:
            project.test_session.stop()

    @pytest.mark.integration  # type: ignore
    def test__test_session_running__start_test_session__test_session_remained_started(
        self, app: Application, project_with_produced_data: Project
    ) -> None:
        project = project_with_produced_data
        project.test_session.start()
        try:
            started_again = project.test_session.start()

            assert started_again is False
            assert TestSessionState.RUNNING == project.test_session.state
        finally:
            project.test_session.stop()

    @pytest.mark.integration  # type: ignore
    def test__test_session_idle__stop_test_session__test_session_not_stopped(
        self, app: Application, project_with_produced_data: Project
    ) -> None:
        project = project_with_produced_data
        stopped = project.test_session.stop()

        assert stopped is False
        assert TestSessionState.IDLE == project.test_session.state

    @pytest.mark.integration  # type: ignore
    def test__test_session_running__stop_test_session__test_session_stopped(
        self, app: Application, project_with_produced_data: Project
    ) -> None:
        project = project_with_produced_data
        project.test_session.start()

        stopped = project.test_session.stop()

        assert stopped is True
        assert TestSessionState.IDLE == project.test_session.state

    @pytest.mark.integration  # type: ignore
    def test__test_session_running__add_note__note_added(self, app: Application) -> None:
        with open_project(app, "ProjectWithProducedData") as project:
            logging_specification = project.open_logging_specification_document()
            with TemporaryDirectory() as temp_dir:
                logging_specification.set_log_file_base_path(temp_dir)
                logging_specification.set_log_file_name("AddNoteTest.tdms")
                project.test_session.start()

                note_str = "Some note about what is happening in the test"
                project.test_session.add_note(note_str)

                project.test_session.stop()
                self._verify_tdms_file_has_note(temp_dir, "AddNoteTest.tdms", note_str)

    def _verify_tdms_file_has_note(
        self, log_file_base_path: str, log_file_name: str, expected_note_contents: str
    ) -> None:
        log_file_path = Path(log_file_base_path) / log_file_name
        with TdmsFile.open(str(log_file_path)) as tdms_file:
            user_notes_group = tdms_file["Test Information"]
            user_notes_channel = user_notes_group["User Notes"]
            assert user_notes_channel is not None
            user_notes_time_channel = user_notes_group["User Notes_time"]
            assert user_notes_time_channel is not None
            assert 1 == len(user_notes_channel)
            assert expected_note_contents == user_notes_channel[0]

    @pytest.mark.integration  # type: ignore
    def test__test_session_idle__add_note__exception_raised(
        self, app: Application, project_with_produced_data: Project
    ) -> None:
        with pytest.raises(FlexLoggerError):
            project_with_produced_data.test_session.add_note("Nope")

    @pytest.mark.integration  # type: ignore
    def test__close_project__start_test__exception_raised(self, app: Application) -> None:
        project = app.open_project(get_project_path("ProjectWithProducedData"))
        project.close()
        with pytest.raises(FlexLoggerError):
            project.test_session.start()

    @pytest.mark.integration  # type: ignore
    def test__add_prompt_on_start_property__start_test__app_pops_dialog(self) -> None:
        # We are testing that if a property is "prompt on start" then FlexLogger should
        # pop up the dialog to set that property when we start a test.
        # This is tricky to test because this means the call to test_session.start() will
        # hang waiting for the dialog to finish.  This is as intended.
        #
        # Since we need to kill the call after we're done, it's safer to run this in a separate
        # process, and we keep track of the results in this test.
        with TemporaryDirectory() as temp_dir:
            script_path = (
                Path(os.path.dirname(os.path.realpath(__file__))) / "start_test_separate_process.py"
            )

            with copy_project("ProjectWithProducedData") as new_project_path:
                process = None
                try:
                    process = subprocess.Popen(
                        [sys.executable, str(script_path), str(new_project_path), str(temp_dir)]
                    )
                    # We need to allow time for FlexLogger to launch and the project to open,
                    # so make sure this timeout is relatively high.
                    end_timeout_time = time.time() + 40
                    while time.time() < end_timeout_time:
                        # process.poll() will return a number if the process has exited
                        assert process.poll() is None
                    # Make sure the test hasn't started (so we haven't written any data)
                    assert (Path(temp_dir) / "ShouldNotExist.tdms").exists() is False
                finally:
                    kill_all_open_flexloggers()
                    if process is not None:
                        process.kill()
