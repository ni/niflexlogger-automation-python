from flexlogger._channel_specification_document import ChannelSpecificationDocument
from flexlogger._logging_specification_document import LoggingSpecificationDocument
from flexlogger._screen_document import ScreenDocument
from flexlogger._test_session import TestSession
from flexlogger._test_specification_document import TestSpecificationDocument
from grpc import Channel, RpcError

from ._flexlogger_error import FlexLoggerError
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
        try:
            response = stub.OpenChannelSpecificationDocument(
                Project_pb2.OpenChannelSpecificationDocumentRequest(project=self._identifier)
            )
            return ChannelSpecificationDocument(self._channel, response.document_identifier)
        except RpcError as rpc_error:
            raise FlexLoggerError("Failed to open channel specification document") from rpc_error

    def open_logging_specification_document(self) -> LoggingSpecificationDocument:
        stub = Project_pb2_grpc.ProjectStub(self._channel)
        try:
            response = stub.OpenLoggingSpecificationDocument(
                Project_pb2.OpenLoggingSpecificationDocumentRequest(project=self._identifier)
            )
            return LoggingSpecificationDocument(self._channel, response.document_identifier)
        except RpcError as rpc_error:
            raise FlexLoggerError("Failed to open logging specification document") from rpc_error

    def open_screen_document(self, filename: str) -> ScreenDocument:
        stub = Project_pb2_grpc.ProjectStub(self._channel)
        try:
            response = stub.OpenScreenDocument(
                Project_pb2.OpenScreenDocumentRequest(
                    project=self._identifier, screen_name=filename
                )
            )
            return ScreenDocument(self._channel, response.document_identifier)
        except RpcError as rpc_error:
            raise FlexLoggerError("Failed to open screen document") from rpc_error

    def open_test_specification_document(self) -> TestSpecificationDocument:
        stub = Project_pb2_grpc.ProjectStub(self._channel)
        try:
            response = stub.OpenTestSpecificationDocument(
                Project_pb2.OpenTestSpecificationDocumentRequest(project=self._identifier)
            )
            return TestSpecificationDocument(self._channel, response.document_identifier)
        except RpcError as rpc_error:
            raise FlexLoggerError("Failed to open test specification document") from rpc_error

    def close(self, allow_prompts: bool) -> None:
        stub = Project_pb2_grpc.ProjectStub(self._channel)
        try:
            stub.Close(Project_pb2.CloseProjectRequest(allow_prompts=allow_prompts))
        except RpcError as rpc_error:
            raise FlexLoggerError("Failed to close project") from rpc_error

    @property
    def test_session(self) -> TestSession:
        return self._test_session
