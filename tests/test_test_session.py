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


class TestTestSession:
    @pytest.mark.integration  # type: ignore
    @pytest.mark.parametrize(
        "project_name,expected_state",
        [
            ("DefaultProject", TestSessionState.NO_VALID_LOGGED_CHANNELS),
            ("ProjectWithError", TestSessionState.INVALID_CONFIGURATION),
        ],
    )  # type: ignore
    def test__open_project__get_test_session_state__state_matches_project(
        self, project_name: str, expected_state: TestSessionState, app: Application
    ) -> None:
        with open_project(app, project_name) as project:
            assert expected_state == project.test_session.state

    @pytest.mark.integration  # type: ignore
    @pytest.mark.parametrize("project_name", ["DefaultProject", "ProjectWithError"])  # type: ignore
    def test__open_project_that_cannot_be_started__start_test_session__exception_raised(
        self, project_name: str, app: Application
    ) -> None:
        with open_project(app, project_name) as project:
            with pytest.raises(FlexLoggerError):
                project.test_session.start()
