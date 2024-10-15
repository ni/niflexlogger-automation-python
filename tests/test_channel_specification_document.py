from datetime import datetime, timedelta, timezone
from time import sleep
from typing import Iterator

import pytest  # type: ignore
from flexlogger.automation import (
    Application,
    ChannelDataPoint,
    ChannelSpecificationDocument,
    DataRateLevel,
    FlexLoggerError,
)

from .utils import get_project_path, open_project


@pytest.fixture(scope="class")
def channels_with_produced_data(app: Application) -> Iterator[ChannelSpecificationDocument]:
    """Fixture for opening the channel specification document for ProjectWithProducedData.

    This is useful to improve test time by not opening/closing this project in every test.
    """
    with open_project(app, "ProjectWithProducedData") as project:
        yield project.open_channel_specification_document()


class TestChannelSpecificationDocument:
    @pytest.mark.integration  # type: ignore
    def test__get_channel_names__all_names_returned(self, app: Application) -> None:
        with open_project(app, "ProjectWithProducedData") as project:
            channel_specification = project.open_channel_specification_document()
            produced_data_channel_names = channel_specification.get_channel_names()
        with open_project(app, "ProjectWithTestProperties") as project:
            channel_specification = project.open_channel_specification_document()
            test_properties_channel_names = channel_specification.get_channel_names()
        assert "Channel 1" in produced_data_channel_names
        assert "Channel 2" in produced_data_channel_names
        produced_data_channel_names.remove("Channel 1")
        produced_data_channel_names.remove("Channel 2")
        assert sorted(produced_data_channel_names) == sorted(test_properties_channel_names)

    @pytest.mark.integration  # type: ignore
    def test__project_with_channels__get_value__values_are_changing_and_timestamps_incrementing(
        self, app: Application, channels_with_produced_data: ChannelSpecificationDocument
    ) -> None:
        channel_specification = channels_with_produced_data
        first_channel_value = channel_specification.get_channel_value("Channel 1")
        sleep(0.5)
        second_channel_value = channel_specification.get_channel_value("Channel 1")

        assert "Channel 1" == first_channel_value.name
        assert "Channel 1" == second_channel_value.name
        assert first_channel_value.value != second_channel_value.value
        assert first_channel_value.timestamp < second_channel_value.timestamp

    @pytest.mark.integration  # type: ignore
    def test__get_channel_value_for_channel_that_does_not_exist__exception_raised(
        self, app: Application, channels_with_produced_data: ChannelSpecificationDocument
    ) -> None:
        channel_specification = channels_with_produced_data
        with pytest.raises(FlexLoggerError):
            channel_specification.get_channel_value("Not a channel")

    @pytest.mark.integration  # type: ignore
    def test__project_with_writable_channels__set_channel_value__channel_value_updated(
        self, app: Application
    ) -> None:
        with open_project(app, "ProjectWithSwitchboard") as project:
            channel_specification = project.open_channel_specification_document()
            now = datetime.now(timezone.utc)
            channel_specification.set_channel_value("Switch 42", 84.5)

            updated_value = channel_specification.get_channel_value("Switch 42")

            assert "Switch 42" == updated_value.name
            assert 84.5 == updated_value.value
            assert updated_value.timestamp >= now
            assert updated_value.timestamp - now < timedelta(minutes=1)

    @pytest.mark.integration  # type: ignore
    def test__set_channel_value_for_channel_that_does_not_exist__exception_raised(
        self, app: Application, channels_with_produced_data: ChannelSpecificationDocument
    ) -> None:
        channel_specification = channels_with_produced_data
        with pytest.raises(FlexLoggerError):
            channel_specification.set_channel_value("Not a channel", 42)

    @pytest.mark.integration  # type: ignore
    def test__set_channel_value_for_readonly_channel__exception_raised(
        self, app: Application, channels_with_produced_data: ChannelSpecificationDocument
    ) -> None:
        channel_specification = channels_with_produced_data
        with pytest.raises(FlexLoggerError):
            channel_specification.set_channel_value("Channel 1", 42)

    @pytest.mark.integration  # type: ignore
    def test__close_project_with_channels__get_value__exception_raised(
        self, app: Application
    ) -> None:
        project = app.open_project(get_project_path("ProjectWithProducedData"))
        channel_specification = project.open_channel_specification_document()
        project.close()
        with pytest.raises(FlexLoggerError):
            channel_specification.get_channel_value("Channel 1")

    @pytest.mark.integration  # type: ignore
    def test__channeldatapoint_repr__returns_correct_string(self) -> None:
        channel_data_point = ChannelDataPoint("Channel", 2.5, datetime.now())
        expected_repr = 'flexlogger.automation.ChannelDataPoint("Channel", 2.500000, %s)' % repr(
            channel_data_point.timestamp
        )
        assert expected_repr == repr(channel_data_point)

    @pytest.mark.integration  # type: ignore
    def test__project_with_writable_channels__disable_channel__channel_disabled(
        self, app: Application
    ) -> None:
        with open_project(app, "ProjectWithSwitchboard") as project:
            channel_specification = project.open_channel_specification_document()

            channel_specification.set_channel_enabled("Switch 42", False)

            channel_enabled = channel_specification.is_channel_enabled("Switch 42")

            assert not channel_enabled

    @pytest.mark.integration  # type: ignore
    def test__set_channel_enabled_for_channel_that_does_not_exist__exception_raised(
        self, app: Application, channels_with_produced_data: ChannelSpecificationDocument
    ) -> None:
        channel_specification = channels_with_produced_data
        with pytest.raises(FlexLoggerError):
            channel_specification.set_channel_enabled("Not a channel", True)

    @pytest.mark.integration  # type: ignore
    def test__set_channel_enabled_for_readonly_channel__exception_raised(
        self, app: Application, channels_with_produced_data: ChannelSpecificationDocument
    ) -> None:
        channel_specification = channels_with_produced_data
        with pytest.raises(FlexLoggerError):
            channel_specification.set_channel_enabled("Channel 1", False)

    @pytest.mark.integration  # type: ignore
    def test__project_with_writable_channels__disable_channel_logging__channel_logging_disabled(
        self, app: Application
    ) -> None:
        with open_project(app, "ProjectWithSwitchboard") as project:
            channel_specification = project.open_channel_specification_document()

            channel_specification.set_channel_logging_enabled("Switch 42", False)

            channel_logging_enabled = channel_specification.is_channel_logging_enabled("Switch 42")

            assert not channel_logging_enabled

    @pytest.mark.integration  # type: ignore
    def test__project_with_writable_channels__channel_logging_enabled(
        self, app: Application
    ) -> None:
        with open_project(app, "ProjectWithSwitchboard") as project:
            channel_specification = project.open_channel_specification_document()

            channel_logging_enabled = channel_specification.is_channel_logging_enabled("Switch 42")

            assert channel_logging_enabled

    @pytest.mark.integration  # type: ignore
    def test__set_channel_logging_enabled_for_channel_that_does_not_exist__exception_raised(
        self, app: Application, channels_with_produced_data: ChannelSpecificationDocument
    ) -> None:
        channel_specification = channels_with_produced_data
        with pytest.raises(FlexLoggerError):
            channel_specification.set_channel_logging_enabled("Not a channel", True)

    @pytest.mark.integration  # type: ignore
    def test__set_channel_logging_enabled_for_readonly_channel__exception_raised(
        self, app: Application, channels_with_produced_data: ChannelSpecificationDocument
    ) -> None:
        channel_specification = channels_with_produced_data
        with pytest.raises(FlexLoggerError):
            channel_specification.set_channel_logging_enabled("Channel 1", False)

    @pytest.mark.integration  # type: ignore
    def test__project_with_channels__set_data_rate__data_rate_updated(
        self, app: Application, channels_with_produced_data: ChannelSpecificationDocument
    ) -> None:
        channel_specification = channels_with_produced_data

        channel_specification.set_data_rate(DataRateLevel.SLOW, 2)

        data_rate = channel_specification.get_data_rate(DataRateLevel.SLOW)
        assert data_rate == 2

    @pytest.mark.integration  # type: ignore
    def test__project_with_channels__get_data_rate_level_on_invalid_channel__exception_raised(
        self, app: Application, channels_with_produced_data: ChannelSpecificationDocument
    ) -> None:
        channel_specification = channels_with_produced_data

        with pytest.raises(FlexLoggerError):
            channel_specification.get_module_data_rate_level("Channel 1")

    @pytest.mark.integration  # type: ignore
    def test__project_with_channels__set_data_rate_level_on_invalid_channel__exception_raised(
        self, app: Application, channels_with_produced_data: ChannelSpecificationDocument
    ) -> None:
        channel_specification = channels_with_produced_data

        with pytest.raises(FlexLoggerError):
            channel_specification.set_module_data_rate_level("Channel 1", DataRateLevel.SLOW)
