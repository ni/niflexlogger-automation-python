from flexlogger._channel_specification_document import ChannelSpecificationDocument
from flexlogger._logging_specification_document import LoggingSpecificationDocument
from flexlogger._screen_document import ScreenDocument
from flexlogger._test_session import TestSession
from flexlogger._test_specification_document import TestSpecificationDocument
from grpc import Channel

from .proto import (
    Project_pb2,  # type: ignore
    Project_pb2_grpc,  # type: ignore
)
from .proto.Identifiers_pb2 import ProjectIdentifier


class Project:
    def __init__(self, channel: Channel, identifier: ProjectIdentifier) -> None:
        self._channel = channel
        self._identifier = identifier
        self._test_session = TestSession(self._channel)

    def open_channel_specification_document(self) -> ChannelSpecificationDocument:
        stub = Project_pb2_grpc.ProjectStub(self._channel)
        response = stub.OpenChannelSpecificationDocument(
            Project_pb2.OpenChannelSpecificationDocumentRequest(project=self._identifier)
        )
        return ChannelSpecificationDocument(self._channel, response.document_identifier)

    def open_logging_specification_document(self) -> LoggingSpecificationDocument:
        stub = Project_pb2_grpc.ProjectStub(self._channel)
        response = stub.OpenLoggingSpecificationDocument(
            Project_pb2.OpenLoggingSpecificationDocumentRequest(project=self._identifier)
        )
        return LoggingSpecificationDocument(self._channel, response.document_identifier)

    def open_screen_document(self, filename: str) -> ScreenDocument:
        stub = Project_pb2_grpc.ProjectStub(self._channel)
        response = stub.OpenScreenDocument(
            Project_pb2.OpenScreenDocumentRequest(project=self._identifier, screen_name=filename)
        )
        return ScreenDocument(self._channel, response.document_identifier)

    def open_test_specification_document(self) -> TestSpecificationDocument:
        stub = Project_pb2_grpc.ProjectStub(self._channel)
        response = stub.OpenTestSpecificationDocument(
            Project_pb2.OpenTestSpecificationDocumentRequest(project=self._identifier)
        )
        return TestSpecificationDocument(self._channel, response.document_identifier)

    def close(self, allow_prompts: bool) -> None:
        stub = Project_pb2_grpc.ProjectStub(self._channel)
        stub.Close(Project_pb2.CloseProjectRequest(allow_prompts=allow_prompts))

    @property
    def test_session(self) -> TestSession:
        return self._test_session
