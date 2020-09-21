from typing import Iterator

import pytest  # type: ignore
from flexlogger.automation import (
    Application,
    FlexLoggerError,
    LoggingSpecificationDocument,
    TestProperty,
)

from .utils import get_project_path, open_project


@pytest.fixture(scope="module")
def logging_spec_with_test_properties(app: Application) -> Iterator[LoggingSpecificationDocument]:
    """Fixture for opening the logging specification document for ProjectWithProducedData.

    This is useful to improve test time by not opening/closing this project in every test.
    Note that using this fixture means the test may not modify the project.
    """
    with open_project(app, "ProjectWithTestProperties") as project:
        yield project.open_logging_specification_document()


class TestLoggingSpecificationDocument:
    @pytest.mark.integration  # type: ignore
    def test__open_project__get_logging_path__logging_path_matches_user_setting(
        self, app: Application
    ) -> None:
        with open_project(app, "ProjectWithUpdatedLoggingPath") as project:
            logging_specification = project.open_logging_specification_document()

            assert r"C:\MyDataGoesHere" == logging_specification.get_log_file_base_path()
            assert r"MyData.tdms" == logging_specification.get_log_file_name()

    @pytest.mark.integration  # type: ignore
    def test__open_project__set_logging_path__logging_path_updates(self, app: Application) -> None:
        with open_project(app, "ProjectWithUpdatedLoggingPath") as project:
            logging_specification = project.open_logging_specification_document()

            logging_specification.set_log_file_base_path(r"C:\MyDataGoesThere")
            logging_specification.set_log_file_name(r"EvenMoreData.tdms")

            assert r"C:\MyDataGoesThere" == logging_specification.get_log_file_base_path()
            assert r"EvenMoreData.tdms" == logging_specification.get_log_file_name()

    @pytest.mark.integration  # type: ignore
    def test__start_test_session__set_logging_base_path__exception_raised(
        self, app: Application
    ) -> None:
        with open_project(app, "ProjectWithProducedData") as project:
            project.test_session.start()
            logging_specification = project.open_logging_specification_document()

            with pytest.raises(FlexLoggerError):
                logging_specification.set_log_file_base_path(r"C:\NewBasePath")

    @pytest.mark.integration  # type: ignore
    def test__start_test_session__get_logging_base_path__no_exception_raised(
        self, app: Application
    ) -> None:
        with open_project(app, "ProjectWithProducedData") as project:
            project.test_session.start()
            logging_specification = project.open_logging_specification_document()

            base_path = logging_specification.get_log_file_base_path()
            assert base_path is not None

    @pytest.mark.integration  # type: ignore
    def test__start_test_session__set_logging_name__exception_raised(
        self, app: Application
    ) -> None:
        with open_project(app, "ProjectWithProducedData") as project:
            project.test_session.start()
            logging_specification = project.open_logging_specification_document()

            with pytest.raises(FlexLoggerError):
                logging_specification.set_log_file_name(r"NewName")

    @pytest.mark.integration  # type: ignore
    def test__start_test_session__get_logging_name__no_exception_raised(
        self, app: Application
    ) -> None:
        with open_project(app, "ProjectWithProducedData") as project:
            project.test_session.start()
            logging_specification = project.open_logging_specification_document()

            name = logging_specification.get_log_file_name()
            assert name is not None

    @pytest.mark.integration  # type: ignore
    def test__open_project__get_test_properties__all_properties_returned(
        self, app: Application, logging_spec_with_test_properties: LoggingSpecificationDocument
    ) -> None:
        properties = logging_spec_with_test_properties.get_test_properties()

        assert 5 == len(properties)
        self.assert_property_matches(properties[0], "Operator", "bparrott", False)
        self.assert_property_matches(
            properties[1], "DUT", "Serial number: <replace with serial number>", True
        )
        self.assert_property_matches(properties[2], "Property", "", False)
        self.assert_property_matches(
            properties[3], "Best Configuration Based Data Logging Software", "FlexLogger", False
        )
        self.assert_property_matches(properties[4], "Who you gonna call?", "Ghostbusters", False)

    @pytest.mark.integration  # type: ignore
    def test__open_project__get_test_properties__get_test_property_matches(
        self, app: Application, logging_spec_with_test_properties: LoggingSpecificationDocument
    ) -> None:
        properties = logging_spec_with_test_properties.get_test_properties()

        for prop in properties:
            actual_prop = logging_spec_with_test_properties.get_test_property(prop.property_name)
            self.assert_property_matches(
                actual_prop, prop.property_name, prop.property_value, prop.prompt_on_start
            )

    @pytest.mark.integration  # type: ignore
    def test__open_project__get_test_property_that_does_not_exist__exception_raised(
        self, app: Application, logging_spec_with_test_properties: LoggingSpecificationDocument
    ) -> None:
        with open_project(app, "ProjectWithTestProperties") as project:
            logging_specification = project.open_logging_specification_document()
            with pytest.raises(FlexLoggerError):
                logging_specification.get_test_property("DoesNotExist")

    @pytest.mark.integration  # type: ignore
    def test__open_project__set_test_property_that_does_exist__property_is_updated(
        self, app: Application
    ) -> None:
        with open_project(app, "ProjectWithTestProperties") as project:
            logging_specification = project.open_logging_specification_document()
            assert 5 == len(logging_specification.get_test_properties())

            logging_specification.set_test_property(
                TestProperty("Property", "New Property Value", True)
            )

            assert 5 == len(logging_specification.get_test_properties())
            new_prop = logging_specification.get_test_property("Property")
            self.assert_property_matches(new_prop, "Property", "New Property Value", True)

    @pytest.mark.integration  # type: ignore
    def test__open_project__set_test_property_that_does_not_exist__property_is_added(
        self, app: Application
    ) -> None:
        with open_project(app, "ProjectWithTestProperties") as project:
            logging_specification = project.open_logging_specification_document()
            assert 5 == len(logging_specification.get_test_properties())

            logging_specification.set_test_property(
                TestProperty("New Property", "some value", False)
            )

            assert 6 == len(logging_specification.get_test_properties())
            new_prop = logging_specification.get_test_property("New Property")
            self.assert_property_matches(new_prop, "New Property", "some value", False)

    @pytest.mark.integration  # type: ignore
    def test__start_test_session__set_test_property__exception_raised(
        self, app: Application
    ) -> None:
        with open_project(app, "ProjectWithProducedData") as project:
            project.test_session.start()
            logging_specification = project.open_logging_specification_document()

            with pytest.raises(FlexLoggerError):
                logging_specification.set_test_property(TestProperty("Nope", "Sorry", True))

    @pytest.mark.integration  # type: ignore
    @pytest.mark.parametrize("name", ["", "12UCannotDoThat", "@!:.#IllegalChars"])  # type: ignore
    def test__set_test_property_with_invalid_name__exception_raised(
        self, app: Application, name: str
    ) -> None:
        with open_project(app, "ProjectWithTestProperties") as project:
            logging_specification = project.open_logging_specification_document()

            with pytest.raises(FlexLoggerError):
                logging_specification.set_test_property(TestProperty(name, "nope", False))

    @pytest.mark.integration  # type: ignore
    def test__remove_test_property__test_property_removed(self, app: Application) -> None:
        with open_project(app, "ProjectWithTestProperties") as project:
            logging_specification = project.open_logging_specification_document()
            existing_properties = logging_specification.get_test_properties()
            assert 5 == len(existing_properties)
            assert "Property" in (prop.property_name for prop in existing_properties)

            logging_specification.remove_test_property("Property")

            new_properties = logging_specification.get_test_properties()
            assert 4 == len(new_properties)
            assert "Property" not in (prop.property_name for prop in new_properties)
            with pytest.raises(FlexLoggerError):
                logging_specification.get_test_property("Property")

    @pytest.mark.integration  # type: ignore
    def test__remove_test_property_that_does_not_exist__exception_raised(
        self, app: Application
    ) -> None:
        with open_project(app, "ProjectWithTestProperties") as project:
            logging_specification = project.open_logging_specification_document()
            with pytest.raises(FlexLoggerError):
                logging_specification.remove_test_property("DoesNotExist")

    @pytest.mark.integration  # type: ignore
    def test__start_test_session__remove_test_property__exception_raised(
        self, app: Application
    ) -> None:
        with open_project(app, "ProjectWithProducedData") as project:
            project.test_session.start()
            logging_specification = project.open_logging_specification_document()

            with pytest.raises(FlexLoggerError):
                logging_specification.remove_test_property("Property")

    @pytest.mark.integration  # type: ignore
    def test__close_project__get_test_properties__exception_raised(self, app: Application) -> None:
        project = app.open_project(get_project_path("ProjectWithProducedData"))
        logging_specification = project.open_logging_specification_document()
        project.close(allow_prompts=False)
        with pytest.raises(FlexLoggerError):
            logging_specification.get_test_properties()

    def assert_property_matches(
        self,
        test_property: TestProperty,
        expected_name: str,
        expected_value: str,
        expected_prompt_on_start: bool,
    ) -> None:
        assert expected_name == test_property.property_name
        assert expected_value == test_property.property_value
        assert expected_prompt_on_start == test_property.prompt_on_start
