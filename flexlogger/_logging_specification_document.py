from typing import List

from grpc import Channel, RpcError

from ._flexlogger_error import FlexLoggerError
from ._test_property import TestProperty
from .proto import LoggingSpecificationDocument_pb2, LoggingSpecificationDocument_pb2_grpc
from .proto.Identifiers_pb2 import ElementIdentifier


class LoggingSpecificationDocument:
    """Represents a document that describes how data is logged.

    This should not be created directly; instead, the return value of
    :meth:`.Project.open_logging_specification_document` should be used.
    """

    def __init__(self, channel: Channel, identifier: ElementIdentifier) -> None:
        self._channel = channel
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
        except RpcError as rpc_error:
            raise FlexLoggerError("Failed to get log file base path") from rpc_error

    def set_log_file_base_path(self, log_file_base_path: str) -> None:
        """Set the log file base path.

        Args:
            log_file_base_path: The log file base path to set

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
        except RpcError as rpc_error:
            raise FlexLoggerError("Failed to set log file base path") from rpc_error

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
        except RpcError as rpc_error:
            raise FlexLoggerError("Failed to get log file name") from rpc_error

    def set_log_file_name(self, log_file_name: str) -> None:
        """Set the log file name.

        Args:
            log_file_name: The log file name to set

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
        except RpcError as rpc_error:
            raise FlexLoggerError("Failed to set log file name") from rpc_error

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
            property_name=test_property.property_name,
            property_value=test_property.property_value,
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
        except RpcError as rpc_error:
            raise FlexLoggerError("Failed to get test properties") from rpc_error

    def get_test_property(self, test_property_name: str) -> TestProperty:
        """Get the test property with the specified name.

        Throws a :class:`FlexLoggerError` if a property with the
        specified name does not exist.

        Args:
            test_property_name: The name of the test property to get information about.

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
        except RpcError as rpc_error:
            raise FlexLoggerError("Failed to get test property") from rpc_error

    def set_test_property(self, test_property: TestProperty) -> None:
        """Set the information for a test property.

        This method can be used to add a new test property or to modify an existing
        test property.

        Args:
            test_property: Information defining the test property to set. If a test property
                already exists with the same :attr:`~TestProperty.property_name`, that test property
                will be updated with the other test property's information. Otherwise, a new
                test property will be created to reflect the specified test information.

        Raises:
            FlexLoggerError: if setting the property fails.
        """
        stub = LoggingSpecificationDocument_pb2_grpc.LoggingSpecificationDocumentStub(self._channel)
        try:
            stub.SetTestProperty(
                LoggingSpecificationDocument_pb2.SetTestPropertyRequest(
                    document_identifier=self._identifier,
                    test_property=self._convert_from_test_property(test_property),
                )
            )
        except RpcError as rpc_error:
            raise FlexLoggerError("Failed to set test property") from rpc_error

    def remove_test_property(self, test_property_name: str) -> None:
        """Removes the test property with the specified name.

        Args:
            test_property_name: The name of the test property to remove.

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
        except RpcError as rpc_error:
            raise FlexLoggerError("Failed to remove test property") from rpc_error
