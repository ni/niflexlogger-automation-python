from google.protobuf.duration_pb2 import Duration
from google.protobuf.timestamp_pb2 import Timestamp
import datetime
from datetime import timezone
from dateutil import parser
from dateutil import tz
from grpc import Channel, RpcError
from typing import Callable, List

from ._flexlogger_error import FlexLoggerError
from ._start_trigger_condition import StartTriggerCondition
from ._stop_trigger_condition import StopTriggerCondition
from ._test_property import TestProperty
from ._log_file_type import LogFileType
from ._value_change_condition import ValueChangeCondition
from .proto import LoggingSpecificationDocument_pb2, LoggingSpecificationDocument_pb2_grpc
from .proto.Identifiers_pb2 import ElementIdentifier

from .proto.LoggingSpecificationDocument_pb2 import LogFileType as LogFileType_pb2

LOG_FILE_TYPE_MAP = {
    LogFileType.TDMS: LogFileType_pb2.TDMS,
    LogFileType.CSV: LogFileType_pb2.CSV,
    LogFileType.TDMS_BACKUP_FILES: LogFileType_pb2.TDMS_BACKUP,
}

class LoggingSpecificationDocument:
    """Represents a document that describes how data is logged.

    Do not create this class directly; instead, use the return value of
    :meth:`.Project.open_logging_specification_document`.
    """

    def __init__(
        self,
        channel: Channel,
        raise_if_application_closed: Callable[[], None],
        identifier: ElementIdentifier,
    ) -> None:
        self._channel = channel
        self._raise_if_application_closed = raise_if_application_closed
        self._identifier = identifier

    def get_log_file_base_path(self) -> str:
        """Get the log file base path.

        Returns:
            The base path for the log file.

        Raises:
            FlexLoggerError: if getting the log file base path fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            response = stub.GetLogFileBasePath(
                LoggingSpecificationDocument_pb2.GetLogFileBasePathRequest(
                    document_identifier=self._identifier
                )
            )
            return response.log_file_base_path
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get log file base path") from error

    def get_resolved_log_file_base_path(self) -> str:
        """Get the resolved log file base path.

        Returns:
            The resolved base path for the log file.
            The resolved base path will have any placeholders replaced with
            actual values. Note that time sourced placeholders such as
            {Second} are resolved at the time of the call, and may resolve
            to a different time on a subsequent call or when a log file is created.

        Raises:
            FlexLoggerError: if getting the resolved log file base path fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            response = stub.GetResolvedLogFileBasePath(
                LoggingSpecificationDocument_pb2.GetResolvedLogFileBasePathRequest(
                    document_identifier=self._identifier
                )
            )
            return response.resolved_log_file_base_path
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get resolved log file base path") from error

    def set_log_file_base_path(self, log_file_base_path: str) -> None:
        """Set the log file base path.

        Args:
            log_file_base_path: The log file base path.

        Raises:
            FlexLoggerError: if setting the log file base path fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            stub.SetLogFileBasePath(
                LoggingSpecificationDocument_pb2.SetLogFileBasePathRequest(
                    document_identifier=self._identifier, log_file_base_path=log_file_base_path
                )
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to set log file base path") from error

    def get_log_file_name(self) -> str:
        """Get the log file name.

        Returns:
            The file name that will be logged to.

        Raises:
            FlexLoggerError: if getting the log file name fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            response = stub.GetLogFileName(
                LoggingSpecificationDocument_pb2.GetLogFileNameRequest(
                    document_identifier=self._identifier
                )
            )
            return response.log_file_name
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get log file name") from error

    def get_resolved_log_file_name(self) -> str:
        """Get the resolved log file name.

        Returns:
            The resolved file name that will be logged to.
            The resolved file name will have any placeholders replaced with
            actual values. Note that time sourced placeholders such as
            {Second} are resolved at the time of the call, and may resolve
            to a different time on a subsequent call or when a log file is created.

        Raises:
            FlexLoggerError: if getting the resolved log file name fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            response = stub.GetResolvedLogFileName(
                LoggingSpecificationDocument_pb2.GetResolvedLogFileNameRequest(
                    document_identifier=self._identifier
                )
            )
            return response.resolved_log_file_name
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get resolved log file name") from error

    def set_log_file_name(self, log_file_name: str) -> None:
        """Set the log file name.

        Args:
            log_file_name: The log file name.

        Raises:
            FlexLoggerError: if setting the log file name fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            stub.SetLogFileName(
                LoggingSpecificationDocument_pb2.SetLogFileNameRequest(
                    document_identifier=self._identifier, log_file_name=log_file_name
                )
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to set log file name") from error

    def get_log_file_description(self) -> str:
        """Get the log file description.

        Returns:
            The description of the log file.

        Raises:
            FlexLoggerError: if getting the log file description fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            response = stub.GetLogFileDescription(
                LoggingSpecificationDocument_pb2.GetLogFileDescriptionRequest(
                    document_identifier=self._identifier
                )
            )
            return response.log_file_description
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get log file description") from error

    def set_log_file_description(self, log_file_description: str) -> None:
        """Set the log file description.

        Args:
            log_file_description: The log file description.

        Raises:
            FlexLoggerError: if setting the log file description fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            stub.SetLogFileDescription(
                LoggingSpecificationDocument_pb2.SetLogFileDescriptionRequest(
                    document_identifier=self._identifier, log_file_description=log_file_description
                )
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to set log file description") from error

    def get_log_files(self, log_file_type: LogFileType) -> List[str]:
        """Get log files in the data files pane of the project.

        Args:
            log_file_type: The type of log files to get.

        Returns:
            A list of the log files in the project.
            The entries are sorted chronologically with the most recent file last.

        Raises:
            FlexLoggerError: if getting the log files fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            response = stub.GetLogFiles(
                LoggingSpecificationDocument_pb2.GetLogFilesRequest(
                    document_identifier=self._identifier,
                    log_file_type = LOG_FILE_TYPE_MAP[log_file_type]
                )
            )
            return [log_file for log_file in response.log_files]
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get data files") from error

    def remove_log_files(self, delete_files: bool = False) -> None:
        """Remove log files from the data files pane of the project.

        Args:
            delete_files: True to delete files on disk, False to remove only from project.

        Raises:
            FlexLoggerError: if removing the log files fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            stub.RemoveLogFiles(
                LoggingSpecificationDocument_pb2.RemoveLogFilesRequest(
                    document_identifier=self._identifier,
                    delete_files=delete_files
                )
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to remove log files") from error

    def _convert_to_test_property(
        self, test_property: LoggingSpecificationDocument_pb2.TestProperty
    ) -> TestProperty:
        return TestProperty(
            test_property.property_name,
            test_property.property_value,
            test_property.prompt_on_start,
        )

    def _convert_from_test_property(
        self, test_property: TestProperty
    ) -> LoggingSpecificationDocument_pb2.TestProperty:
        return LoggingSpecificationDocument_pb2.TestProperty(
            property_name=test_property.name,
            property_value=test_property.value,
            prompt_on_start=test_property.prompt_on_start,
        )

    def get_test_properties(self) -> List[TestProperty]:
        """Get all test properties.

        Returns:
            A list of the test properties on this document.

        Raises:
            FlexLoggerError: if getting the test properties fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            response = stub.GetTestProperties(
                LoggingSpecificationDocument_pb2.GetTestPropertiesRequest(
                    document_identifier=self._identifier
                )
            )
            return [self._convert_to_test_property(x) for x in response.test_properties]
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get test properties") from error

    def set_test_properties(self, test_properties: List[TestProperty]) -> None:
        """Set test properties.

        Args:
            test_properties: A list of test properties to add or modify on this document.

        Raises:
            FlexLoggerError: if setting the test properties fails.
        """
        if len(test_properties) == 0:
            return
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            stub.SetTestProperties(
                LoggingSpecificationDocument_pb2.SetTestPropertiesRequest(
                    document_identifier=self._identifier,
                    test_properties=[self._convert_from_test_property(x) for x in test_properties]
                )
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to set test properties") from error
        
    def get_test_property(self, test_property_name: str) -> TestProperty:
        """Get the test property with the specified name.

        Throws a :class:`FlexLoggerError` if a property with the
        specified name does not exist.

        Args:
            test_property_name: The name of the test property.

        Returns:
            The :class:`TestProperty` with the specified name.

        Raises:
            FlexLoggerError: if a property with the specified name does
                not exist, or if getting the property fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            response = stub.GetTestProperty(
                LoggingSpecificationDocument_pb2.GetTestPropertyRequest(
                    document_identifier=self._identifier, property_name=test_property_name
                )
            )
            return self._convert_to_test_property(response.test_property)
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get test property") from error

    def set_test_property(
        self, property_name: str, property_value: str, prompt_on_start: bool = False
    ) -> None:
        """Set the information for a test property.

        Use this method to add a new test property or to modify an existing
        test property.

        Args:
            property_name: The name of the test property. If a test property
                already exists with the same :attr:`~TestProperty.name`, that test property
                will be updated with the new information passed to this method. Otherwise, a new
                test property will be created to reflect the specified test information.

            property_value: The property value to set.

            prompt_on_start: Whether this property should be set when the test session starts.
                Defaults to False. If this is set to True, the operator should be prompted to
                define this property when the test session starts.

        Raises:
            FlexLoggerError: if setting the property fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            test_property = LoggingSpecificationDocument_pb2.TestProperty(
                property_name=property_name,
                property_value=property_value,
                prompt_on_start=prompt_on_start,
            )
            stub.SetTestProperty(
                LoggingSpecificationDocument_pb2.SetTestPropertyRequest(
                    document_identifier=self._identifier, test_property=test_property
                )
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to set test property") from error

    def remove_test_property(self, test_property_name: str) -> None:
        """Removes the test property with the specified name.

        Args:
            test_property_name: The name of the test property.

        Raises:
            FlexLoggerError: if a property with the specified name does not
                exist, or if removing the property fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            stub.RemoveTestProperty(
                LoggingSpecificationDocument_pb2.RemoveTestPropertyRequest(
                    document_identifier=self._identifier, property_name=test_property_name
                )
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to remove test property") from error

    def get_start_trigger_settings(self):
        """Get the start trigger settings.

        Returns:
            A tuple containing 2 strings:
            - The start trigger condition
            - The start trigger settings
              The object returned varies based on the start trigger condition.
                - When the start trigger condition is TEST_START, the object is None
                - When the start trigger condition is CHANNEL_VALUE_CHANGE, the object is of type ValueChangeCondition
                - When the start trigger condition is ABSOLUTE_TIME, the object is a datetime object containing the test start time.

        Raises:
            FlexLoggerError: if getting the start trigger settings fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            response = stub.GetStartTriggerSettings(
                LoggingSpecificationDocument_pb2.GetStartTriggerSettingsRequest(
                    document_identifier=self._identifier
                )
            )
            start_trigger_condition = StartTriggerCondition.from_start_trigger_condition_pb2(response.start_trigger_condition)
            if start_trigger_condition == StartTriggerCondition.TEST_START:
                return start_trigger_condition, None
            elif start_trigger_condition == StartTriggerCondition.CHANNEL_VALUE_CHANGE:
                value_change_condition = ValueChangeCondition(response.start_trigger_settings)
                return start_trigger_condition, value_change_condition
            else:
                utc_start_time = parser.parse(response.start_trigger_settings)
                utc_start_time = utc_start_time.replace(tzinfo=tz.tzutc())
                start_time = utc_start_time.astimezone(tz.tzlocal())
                return start_trigger_condition, start_time
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get the start trigger settings") from error

    def get_stop_trigger_settings(self) -> tuple[StopTriggerCondition, str]:
        """Get the stop trigger settings.

        Returns:
            A tuple containing 2 strings:
            - The stop trigger condition
            - The stop trigger settings
              The object returned varies based on the stop trigger condition.
                - When the stop trigger condition is TEST_STOP, the object is None
                - When the stop trigger condition is CHANNEL_VALUE_CHANGE, the object is of type ValueChangeCondition
                - When the stop trigger condition is TEST_TIME_ELAPSED, the object is a string containing the test duration

        Raises:
            FlexLoggerError: if getting the stop trigger settings fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            response = stub.GetStopTriggerSettings(
                LoggingSpecificationDocument_pb2.GetStopTriggerSettingsRequest(
                    document_identifier=self._identifier
                )
            )
            stop_trigger_condition = StopTriggerCondition.from_stop_trigger_condition_pb2(response.stop_trigger_condition)
            if stop_trigger_condition == StopTriggerCondition.TEST_STOP:
                return stop_trigger_condition, None
            elif stop_trigger_condition == StopTriggerCondition.CHANNEL_VALUE_CHANGE:
                value_change_condition = ValueChangeCondition(response.stop_trigger_settings)
                return stop_trigger_condition, value_change_condition
            else:
                return stop_trigger_condition, response.stop_trigger_settings
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get the stop trigger settings") from error

    def set_start_trigger_settings_to_test_start(self) -> None:
        """Set the start trigger to Test Start

        Raises:
            FlexLoggerError: if setting the start trigger fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            stub.SetTestStartTriggerSettings(
                LoggingSpecificationDocument_pb2.SetTestStartTriggerSettingsRequest(
                    document_identifier=self._identifier
                )
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to set the start trigger to Test Start") from error

    def set_start_trigger_settings_to_value_change(self, value_change_condition: ValueChangeCondition) -> None:
        """Set the start trigger to Channel Value Change

        Args:
            value_change_condition: The value change parameters as an object of type ValueChangeCondition

        Raises:
            FlexLoggerError: if setting the start trigger fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            stub.SetValueChangeStartTriggerSettings(
                LoggingSpecificationDocument_pb2.SetValueChangeStartTriggerSettingsRequest(
                    document_identifier=self._identifier,
                    channel_name=value_change_condition.channel_name,
                    value_change_type=value_change_condition.value_change_type.to_value_change_type_pb2(),
                    threshold=value_change_condition.threshold,
                    min_value=value_change_condition.min_value,
                    max_value=value_change_condition.max_value,
                    leading_time=value_change_condition.time
                )
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to set the start trigger to Channel Value Change") from error

    def set_start_trigger_settings_to_absolute_time(self, time: datetime) -> None:
        """Set the start trigger to Absolute Time

        Args:
            time: Test start time. If it's timezone-naive, it's assumed to be in UTC.

        Raises:
            FlexLoggerError: if setting the start trigger fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            test_start_time = Timestamp()
            test_start_time.FromDatetime(time)
            stub.SetTimeStartTriggerSettings(
                LoggingSpecificationDocument_pb2.SetTimeStartTriggerSettingsRequest(
                    document_identifier=self._identifier,
                    time=test_start_time
                )
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to set the start trigger to Absolute Time") from error

    def set_stop_trigger_settings_to_test_stop(self) -> None:
        """Set the stop trigger to Test Stop

        Raises:
            FlexLoggerError: if setting the stop trigger fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            stub.SetTestStopTriggerSettings(
                LoggingSpecificationDocument_pb2.SetTestStopTriggerSettingsRequest(
                    document_identifier=self._identifier
                )
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to set the stop trigger to Test Stop") from error

    def set_stop_trigger_settings_to_value_change(self, value_change_condition: ValueChangeCondition) -> None:
        """Set the stop trigger to Channel Value Change

        Args:
            value_change_condition: The value change parameters as an object of type ValueChangeCondition

        Raises:
            FlexLoggerError: if setting the stop trigger fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            stub.SetValueChangeStopTriggerSettings(
                LoggingSpecificationDocument_pb2.SetValueChangeStopTriggerSettingsRequest(
                    document_identifier=self._identifier,
                    channel_name=value_change_condition.channel_name,
                    value_change_type=value_change_condition.value_change_type.to_value_change_type_pb2(),
                    threshold=value_change_condition.threshold,
                    min_value=value_change_condition.min_value,
                    max_value=value_change_condition.max_value,
                    trailing_time=value_change_condition.time
                )
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to set the stop trigger to Channel Value Change") from error

    def set_stop_trigger_settings_to_duration(self, duration: datetime.timedelta) -> None:
        """Set the stop trigger to Test Time Elapsed

        Args:
            duration: The length of time after which to stop the test.

        Raises:
            FlexLoggerError: if setting the stop trigger fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            test_duration = Duration()
            test_duration.FromTimedelta(duration)
            stub.SetTimeStopTriggerSettings(
                LoggingSpecificationDocument_pb2.SetTimeStopTriggerSettingsRequest(
                    document_identifier=self._identifier,
                    duration=test_duration
                )
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to set the stop trigger to Test Time Elapsed") from error

    def is_retriggering_enabled(self) -> bool:
        """Get the re-triggering configuration.

        Returns:
            True if re-triggering is enabled, False otherwise

        Raises:
            FlexLoggerError: if getting the re-triggering configuration fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            response = stub.IsRetriggeringEnabled(
                LoggingSpecificationDocument_pb2.IsRetriggeringEnabledRequest(
                    document_identifier=self._identifier
                )
            )
            return response.is_retriggering_enabled
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get the re-triggering configuration") from error

    def set_retriggering(self, retriggering: bool) -> None:
        """Set the re-triggering configuration.

        Args:
            retriggering: True to enable re-triggering, False to disable it.

        Raises:
            FlexLoggerError: if setting the re-triggering configuration fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            stub.SetRetriggering(
                LoggingSpecificationDocument_pb2.SetRetriggeringRequest(
                    document_identifier=self._identifier,
                    is_retriggering_enabled=retriggering
                )
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to set the re-triggering configuration") from error
