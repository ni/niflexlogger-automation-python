from typing import Callable, List

from grpc import Channel, RpcError

from ._flexlogger_error import FlexLoggerError
from ._test_property import TestProperty
from .proto import LoggingSpecificationDocument_pb2, LoggingSpecificationDocument_pb2_grpc
from .proto.Identifiers_pb2 import ElementIdentifier


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
