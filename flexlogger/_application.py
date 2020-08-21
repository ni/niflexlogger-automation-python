from typing import Optional
import grpc
import mmap
import os
from ._project import Project
import struct
import subprocess
import uuid
from ._utils import _import_module_from_path
# TODO - install this with requirements.txt or pyproject.toml or something to install pywin32
import win32api
import win32event
import winreg

from flexlogger.ConfigurationBasedSoftware.FlexLogger.Automation.FlexLogger.Automation.Protocols import FlexLoggerApplication_pb2
FlexLoggerApplication_pb2_grpc = _import_module_from_path('FlexLoggerApplication_pb2_grpc', os.path.join(os.path.dirname(__file__), 'ConfigurationBasedSoftware/FlexLogger/Automation/FlexLogger.Automation.Protocols/FlexLoggerApplication_pb2_grpc.py'))

_FLEXLOGGER_REGISTRY_KEY_PATH = r"SOFTWARE\National Instruments\FlexLogger"

class Application:
    def __init__(self, connect_to_existing=False) -> None:
        if not connect_to_existing:
            self._server_port = _launch_flexlogger()
        self._channel = grpc.insecure_channel('localhost:%d' % self._server_port)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self) -> None:
        if self._channel is not None:
            self._channel.close()
            self._channel = None
        
    def open_project(self, path: str) -> Project:
        stub = FlexLoggerApplication_pb2_grpc.FlexLoggerApplicationStub(self._channel)
        response = stub.OpenProject(FlexLoggerApplication_pb2.OpenProjectRequest(project_path=path))
        return Project(self._channel, response.project)

def _launch_flexlogger(path: Optional[str] = None) -> int:
    if path is None:
        path = _get_latest_installed_flexlogger_path()
    if path is None:
        raise Exception("Could not determine latest installed path of FlexLogger")
    event_name = uuid.uuid4().hex
    mapped_name = uuid.uuid4().hex

    event = win32event.CreateEvent(None, 0, 0, event_name)
    args = [path]
    args += ["-mappedFileIsReadyEventName=" + event_name, "-mappedFileName=" + mapped_name]
    args += ["-enableAutomationServer", "-allowPrototype"]
    # TODO - close if client closes option
    server_port = None
    try:
        subprocess.Popen(args)
        # TODO - configurable timeout here? Or just something reasonable?
        TIMEOUT_IN_SECONDS = 60
        launched = False
        for _ in range(TIMEOUT_IN_SECONDS):
            object_signaled = win32event.WaitForSingleObject(event, 1000)
            if object_signaled == 0:
                launched = True
                server_port = _read_int_from_mmap(mapped_name)
                break
            elif object_signaled != 258:
                raise Exception("Internal error waiting for FlexLogger to launch. Error code %d" % object_signaled)
        if not launched:
            raise Exception("Timed out waiting for FlexLogger to launch.")
    finally:
        win32api.CloseHandle(event)
    return server_port

def _get_latest_installed_flexlogger_path() -> Optional[str]:
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, _FLEXLOGGER_REGISTRY_KEY_PATH) as flexLoggerKey:
            number_of_subkeys = winreg.QueryInfoKey(flexLoggerKey)[0]
            subkey_names = [winreg.EnumKey(flexLoggerKey, i) for i in range(number_of_subkeys)]
            latest_subkey = sorted([(float(name), name) for name in subkey_names])[-1][1]
            with winreg.OpenKey(flexLoggerKey, latest_subkey) as latest_flexLogger_key:
                return winreg.QueryValueEx(latest_flexLogger_key, "Path")[0]
    except:
        return None

def _read_int_from_mmap(mapped_name: str) -> int:
    with mmap.mmap(-1, 4, tagname=mapped_name, access=mmap.ACCESS_READ) as mapped_file:
        int_bytes = mapped_file.read(4)
        return struct.unpack('i', int_bytes)[0]