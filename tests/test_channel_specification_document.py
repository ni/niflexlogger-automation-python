from datetime import datetime
from time import sleep

import pytest  # type: ignore
from flexlogger import Application, FlexLoggerError

from .utils import open_project


class TestChannelSpecificationDocument:
    @pytest.mark.integration  # type: ignore
    def test__get_channel_names__all_names_returned(self) -> None:
        with Application.launch() as app:
            with open_project(app, "ProjectWithProducedData") as project:
                channel_specification = project.open_channel_specification_document()
                produced_data_channel_names = channel_specification.get_channel_names()
            with open_project(app, "ProjectWithTestProperties") as project:
                channel_specification = project.open_channel_specification_document()
                test_properties_channel_names = channel_specification.get_channel_names()
            # TODO - these names include a bunch of names (from simulated HW?0)
            # C# tests don't have this problem, what's going on?
            assert "Channel 1" in produced_data_channel_names
            assert "Channel 2" in produced_data_channel_names
            assert "df60b754-abb5-442a-9a36-d6d3051ecb46" in produced_data_channel_names
            produced_data_channel_names.remove("Channel 1")
            produced_data_channel_names.remove("Channel 2")
            produced_data_channel_names.remove("df60b754-abb5-442a-9a36-d6d3051ecb46")
            assert sorted(produced_data_channel_names) == sorted(test_properties_channel_names)

    @pytest.mark.integration  # type: ignore
    def test__project_with_channels__get_value__values_are_changing_and_timestamps_incrementing(
        self,
    ) -> None:
        with Application.launch() as app:
            with open_project(app, "ProjectWithProducedData") as project:
                channel_specification = project.open_channel_specification_document()
                first_channel_value = channel_specification.get_double_channel_value("Channel 1")
                sleep(0.5)
                second_channel_value = channel_specification.get_double_channel_value("Channel 1")

                assert "Channel 1" == first_channel_value.channel_name
                assert "Channel 1" == second_channel_value.channel_name
                assert first_channel_value.channel_value != second_channel_value.channel_value
                assert first_channel_value.timestamp < second_channel_value.timestamp

    @pytest.mark.integration  # type: ignore
    def test__get_channel_value_for_channel_that_does_not_exist__exception_raised(self) -> None:
        with Application.launch() as app:
            with open_project(app, "ProjectWithProducedData") as project:
                channel_specification = project.open_channel_specification_document()
                with pytest.raises(FlexLoggerError):
                    channel_specification.get_double_channel_value("Not a channel")

    @pytest.mark.integration  # type: ignore
    def test__project_with_writable_channels__set_channel_value__channel_value_updated(
        self,
    ) -> None:
        with Application.launch() as app:
            with open_project(app, "ProjectWithSwitchboard") as project:
                channel_specification = project.open_channel_specification_document()
                now = datetime.now()
                channel_specification.set_double_channel_value("Switch 42", 84.5)

                updated_value = channel_specification.get_double_channel_value("Switch 42")

                assert "Switch 42" == updated_value.channel_name
                assert 84.5 == updated_value.channel_value
                assert updated_value.timestamp >= now

    @pytest.mark.integration  # type: ignore
    def test__set_channel_value_for_channel_that_does_not_exist__exception_raised(self) -> None:
        with Application.launch() as app:
            with open_project(app, "ProjectWithProducedData") as project:
                channel_specification = project.open_channel_specification_document()
                with pytest.raises(FlexLoggerError):
                    channel_specification.set_double_channel_value("Not a channel", 42)

    @pytest.mark.integration  # type: ignore
    def test__set_channel_value_for_readonly_channel__exception_raised(self) -> None:
        with Application.launch() as app:
            with open_project(app, "ProjectWithProducedData") as project:
                channel_specification = project.open_channel_specification_document()
                with pytest.raises(FlexLoggerError):
                    channel_specification.set_double_channel_value("Channel 1", 42)
