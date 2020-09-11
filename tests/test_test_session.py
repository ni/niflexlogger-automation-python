from typing import Iterator

import pytest  # type: ignore
from flexlogger import Application, FlexLoggerError, Project, TestSessionState

from .utils import open_project


@pytest.fixture(scope="module")
def project_with_produced_data(app: Application) -> Iterator[Project]:
    """Fixture for opening ProjectWithProducedData.

    This is useful to improve test time by not opening/closing this project in every test.
    """
    with open_project(app, "ProjectWithProducedData") as project:
        yield project


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

    # TODO test__test_session_running__add_note__note_added(self) -> None:

    @pytest.mark.integration  # type: ignore
    def test__test_session_idle__add_note__exception_raised(
        self, app: Application, project_with_produced_data: Project
    ) -> None:
        with pytest.raises(FlexLoggerError):
            project_with_produced_data.test_session.add_note("Nope")
