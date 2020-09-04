from typing import Any

from flexlogger._testsession import TestSession

from .proto import (
    Project_pb2,  # type: ignore
    Project_pb2_grpc,  # type: ignore
)


class Project:
    def __init__(self, channel: Any, identifier: Any) -> None:
        self._channel = channel
        self._identifier = identifier
        self._test_session = TestSession(self._channel)

    def close(self, allow_prompts: bool) -> None:
        stub = Project_pb2_grpc.ProjectStub(self._channel)
        stub.Close(Project_pb2.CloseProjectRequest(allow_prompts=allow_prompts))

    @property
    def test_session(self) -> TestSession:
        return self._test_session
