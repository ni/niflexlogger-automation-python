from datetime import datetime, timedelta, timezone
from time import sleep
from typing import Iterator
import time

import pytest  # type: ignore
from flexlogger.automation import (
    Application,
    ChannelDataPoint,
    ChannelSpecificationDocument,
    DataRateLevel,
    FlexLoggerError,
)

from .utils import get_project_path, open_project


class TestChannelSpecificationDocument:
    @pytest.mark.integration  # type: ignore
    def test__channeldatapoint_repr__returns_correct_string(self) -> None:
        channel_data_point = ChannelDataPoint("Channel", 2.5, datetime.now())
        expected_repr = 'flexlogger.automation.ChannelDataPoint("Channel", 2.500000, %s)' % repr(
            channel_data_point.timestamp
        )
        assert expected_repr == repr(channel_data_point)
