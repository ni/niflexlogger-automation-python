import os
from ._utils import _import_module_from_path

from flexlogger.ConfigurationBasedSoftware.FlexLogger.Automation.FlexLogger.Automation.Protocols import Project_pb2
Project_pb2_grpc = _import_module_from_path('Project_pb2_grpc', os.path.join(os.path.dirname(__file__), 'ConfigurationBasedSoftware/FlexLogger/Automation/FlexLogger.Automation.Protocols/Project_pb2_grpc.py'))

class Project:
    def __init__(self, channel, identifier) -> None:
        self._channel = channel
        self._identifier = identifier
    
    def close(self, allow_prompts : bool) -> None:
        stub = Project_pb2_grpc.ProjectStub(self._channel)
        stub.Close(Project_pb2.CloseProjectRequest(allow_prompts=allow_prompts))