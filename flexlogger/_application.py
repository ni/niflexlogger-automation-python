import mmap
import struct
import subprocess
import uuid
from typing import Optional

# TODO - install these with requirements.txt or pyproject.toml or something to install pywin32
import grpc
import win32api
import win32event
import winreg
from flexlogger.proto import (
    FlexLoggerApplication_pb2,
    FlexLoggerApplication_pb2_grpc,
)

from ._project import Project

_FLEXLOGGER_REGISTRY_KEY_PATH = r"SOFTWARE\National Instruments\FlexLogger"


class Application:
    # TODO - this should connect to existing
    def __init__(self) -> None:
        self._server_port = -1
        self._channel = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @classmethod
    def launch(cls, timeout_in_seconds: int = 60) -> "Application":
        application = Application()
        application._server_port = Application._launch_flexlogger(
            timeout_in_seconds=timeout_in_seconds
        )
        application._channel = grpc.insecure_channel("localhost:%d" % application._server_port)
        return application

    def close(self) -> None:
        if self._channel is not None:
            self._channel.close()
            self._channel = None

    def open_project(self, path: str) -> Project:
        stub = FlexLoggerApplication_pb2_grpc.FlexLoggerApplicationStub(self._channel)
        response = stub.OpenProject(FlexLoggerApplication_pb2.OpenProjectRequest(project_path=path))
        return Project(self._channel, response.project)

    @classmethod
    def _launch_flexlogger(cls, timeout_in_seconds: int, path: Optional[str] = None) -> int:
        if path is None:
            path = cls._get_latest_installed_flexlogger_path()
        if path is None:
            raise Exception("Could not determine latest installed path of FlexLogger")
        event_name = uuid.uuid4().hex
        mapped_name = uuid.uuid4().hex

        event = win32event.CreateEvent(None, 0, 0, event_name)
        args = [path]
        args += [
            "-mappedFileIsReadyEventName=" + event_name,
            "-mappedFileName=" + mapped_name,
        ]
        args += ["-enableAutomationServer", "-allowPrototype"]
        # TODO - close if client closes option

        try:
            subprocess.Popen(args)
            for _ in range(timeout_in_seconds):
                object_signaled = win32event.WaitForSingleObject(event, 1000)
                if object_signaled == 0:
                    return cls._read_int_from_mmap(mapped_name)
                elif object_signaled != 258:
                    raise Exception(
                        "Internal error waiting for FlexLogger to launch. Error code %d"
                        % object_signaled
                    )
            raise Exception("Timed out waiting for FlexLogger to launch.")
        finally:
            win32api.CloseHandle(event)

    @classmethod
    def _get_latest_installed_flexlogger_path(cls) -> Optional[str]:
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, _FLEXLOGGER_REGISTRY_KEY_PATH
            ) as flexLoggerKey:
                number_of_subkeys = winreg.QueryInfoKey(flexLoggerKey)[0]
                subkey_names = [winreg.EnumKey(flexLoggerKey, i) for i in range(number_of_subkeys)]
                latest_subkey = sorted([(float(name), name) for name in subkey_names])[-1][1]
                with winreg.OpenKey(flexLoggerKey, latest_subkey) as latest_flexLogger_key:
                    return winreg.QueryValueEx(latest_flexLogger_key, "Path")[0]
        except EnvironmentError:
            return None

    @classmethod
    def _read_int_from_mmap(cls, mapped_name: str) -> int:
        with mmap.mmap(-1, 4, tagname=mapped_name, access=mmap.ACCESS_READ) as mapped_file:
            int_bytes = mapped_file.read(4)
            return struct.unpack("i", int_bytes)[0]
