from typing import Iterator

import pytest
from flexlogger.automation import Application, FlexLoggerError


# This needs to be at class scope because of the order pytest runs tests in.
# It runs a class at a time, so we can't reuse this across classes in case
# tests have run that need to call utils.kill_all_open_flexloggers()
@pytest.fixture(scope="class")
def app() -> Iterator[Application]:
    """Fixture for launching FlexLogger.

    This is useful to improve test time by not launching/closing FlexLogger in every test.
    """
    app = Application.launch()
    yield app
    try:
        app.close()
    except FlexLoggerError:
        # utils.kill_all_open_flexloggers may have killed this process already, that's fine
        pass
