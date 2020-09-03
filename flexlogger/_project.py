from typing import Any

from .proto import (
    Project_pb2,  # type: ignore
    Project_pb2_grpc,  # type: ignore
)


class Project:
    def __init__(self, channel: Any, identifier: Any) -> None:
        self._channel = channel
        self._identifier = identifier

    def close(self, allow_prompts: bool) -> None:
        stub = Project_pb2_grpc.ProjectStub(self._channel)
        stub.Close(Project_pb2.CloseProjectRequest(allow_prompts=allow_prompts))
