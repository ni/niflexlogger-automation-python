import os.path
import pathlib
from typing import Callable
from typing import Optional

from google.protobuf import empty_pb2
from grpc import Channel, RpcError

from ._channel_specification_document import ChannelSpecificationDocument
from ._flexlogger_error import FlexLoggerError
from ._logging_specification_document import LoggingSpecificationDocument
from ._screen_document import ScreenDocument
from ._test_session import TestSession
from ._test_specification_document import TestSpecificationDocument
from .proto import (
    Project_pb2,  # type: ignore
    Project_pb2_grpc,  # type: ignore
)
from .proto.Identifiers_pb2 import ProjectIdentifier


class Project:
    """Represents a FlexLogger project.

    Do not create this class directly; instead, use the return value of
    :meth:`.Application.open_project`.
    """

    def __init__(
        self,
        channel: Channel,
        raise_if_application_closed: Callable[[], None],
        identifier: ProjectIdentifier,
    ) -> None:
        self._channel = channel
        self._raise_if_application_closed = raise_if_application_closed
        self._identifier = identifier
        self._test_session = TestSession(self._channel, raise_if_application_closed)

    def open_channel_specification_document(self) -> ChannelSpecificationDocument:
        """Open the channel specification document in the project.

        Returns:
            The opened document.

        Raises:
            FlexLoggerError: if opening the document fails.
        """
        stub = Project_pb2_grpc.ProjectStub(self._channel)
        try:
            response = stub.OpenChannelSpecificationDocument(
                Project_pb2.OpenChannelSpecificationDocumentRequest(project=self._identifier)
            )
            return ChannelSpecificationDocument(
                self._channel, self._raise_if_application_closed, response.document_identifier
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to open channel specification document") from error

    def open_logging_specification_document(self) -> LoggingSpecificationDocument:
        """Open the logging specification document in the project.

        Returns:
            The opened document.

        Raises:
            FlexLoggerError: if opening the document fails.
        """
        stub = Project_pb2_grpc.ProjectStub(self._channel)
        try:
            response = stub.OpenLoggingSpecificationDocument(
                Project_pb2.OpenLoggingSpecificationDocumentRequest(project=self._identifier)
            )
            return LoggingSpecificationDocument(
                self._channel, self._raise_if_application_closed, response.document_identifier
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to open logging specification document") from error

    def open_screen_document(self, filename: str) -> ScreenDocument:
        """Open the specified screen document in the project.

        Args:
            filename: The name of the screen document to open.  Including
                the .flxscr extension in this argument is optional.

        Returns:
            The opened document.

        Raises:
            FlexLoggerError: if a screen document of the specified name does
                not exist, or if opening the document fails.
        """
        stub = Project_pb2_grpc.ProjectStub(self._channel)
        try:
            response = stub.OpenScreenDocument(
                Project_pb2.OpenScreenDocumentRequest(
                    project=self._identifier, screen_name=filename
                )
            )
            return ScreenDocument(
                self._channel, self._raise_if_application_closed, response.document_identifier
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to open screen document") from error

    def open_test_specification_document(self) -> TestSpecificationDocument:
        """Open the test specification document in the project.

        Returns:
            The opened document.

        Raises:
            FlexLoggerError: if opening the document fails.
        """
        stub = Project_pb2_grpc.ProjectStub(self._channel)
        try:
            response = stub.OpenTestSpecificationDocument(
                Project_pb2.OpenTestSpecificationDocumentRequest(project=self._identifier)
            )
            return TestSpecificationDocument(
                self._channel, self._raise_if_application_closed, response.document_identifier
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to open test specification document") from error

    def close(self) -> None:
        """Close the project.

        Raises:
            FlexLoggerError: if closing the project fails.
        """
        stub = Project_pb2_grpc.ProjectStub(self._channel)
        try:
            stub.Close(Project_pb2.CloseProjectRequest(allow_prompts=False))
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to close project") from error

    def save(self) -> None:
        """Save the project.

        Raises:
            FlexLoggerError: if saving the project fails due to a communication error.
        """
        stub = Project_pb2_grpc.ProjectStub(self._channel)
        try:
            stub.Save(empty_pb2.Empty())
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to save project") from error

    @property
    def test_session(self) -> TestSession:
        """Get the test session for the project."""
        return self._test_session

    @property
    def project_file_path(self) -> Optional[pathlib.Path]:
        """Get the project file path on disk

        Returns: The saved project file path if it exists, None otherwise
        """
        stub = Project_pb2_grpc.ProjectStub(self._channel)
        try:
            response = stub.GetProjectFilePath(
                Project_pb2.GetProjectFilePathRequest(project=self._identifier)
            )
            # return a Path() if the returned path is not empty, otherwise return None
            # pathlib.Path() treats empty string as "current directory" which could be confusing
            return pathlib.Path(response.project_file_path) if response.project_file_path else None
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get project file path") from error

    @property
    def project_name(self) -> Optional[str]:
        """Get the project name

        Returns: The project name if the file path exists, None otherwise
        """
        project_path = self.project_file_path

        return os.path.basename(os.path.splitext(project_path)[0])
