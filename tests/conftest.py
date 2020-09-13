from typing import Iterator

import pytest
from flexlogger import Application


@pytest.fixture(scope="session")
def app() -> Iterator[Application]:
    """Fixture for launching FlexLogger.

    This is useful to improve test time by not launching/closing FlexLogger in every test.
    """
    app = Application.launch()
    yield app
    app.close()
