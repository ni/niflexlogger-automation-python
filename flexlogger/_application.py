import mmap
import struct
import subprocess
import uuid
from pathlib import Path
from typing import Any, Optional, Union

import grpc  # type: ignore
import win32api  # type: ignore
import win32event  # type: ignore
import winreg  # type: ignore

from ._project import Project
from .proto import (
    Application_pb2,  # type: ignore
    Application_pb2_grpc,  # type: ignore
    FlexLoggerApplication_pb2,  # type: ignore
    FlexLoggerApplication_pb2_grpc,  # type: ignore
)

_FLEXLOGGER_REGISTRY_KEY_PATH = r"SOFTWARE\National Instruments\FlexLogger"


class Application:
    # TODO - this should connect to existing
    def __init__(self) -> None:
        self._server_port = -1
        self._channel = None
        self._launched = False

    def __enter__(self) -> "Application":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        # Only exit the application if this was created with Application.launch()
        # If the user wants to override this behavior they can call close()
        # or disconnect() explicitly.
        self._disconnect(exit_application=self._launched)

    @classmethod
    def launch(cls, timeout_in_seconds: int = 60) -> "Application":
        application = Application()
        application._launched = True
        application._server_port = Application._launch_flexlogger(
            timeout_in_seconds=timeout_in_seconds
        )
        application._channel = grpc.insecure_channel("localhost:%d" % application._server_port)
        return application

    def close(self) -> None:
        self._disconnect(exit_application=True)

    def disconnect(self) -> None:
        self._disconnect(exit_application=False)

    def _disconnect(self, exit_application: bool) -> None:
        if self._channel is not None:
            stub = Application_pb2_grpc.ApplicationStub(self._channel)
            stub.Disconnect(Application_pb2.DisconnectRequest(exit_application=exit_application))
            self._channel.close()
            self._channel = None

    def open_project(self, path: Union[str, Path]) -> Project:
        stub = FlexLoggerApplication_pb2_grpc.FlexLoggerApplicationStub(self._channel)
        response = stub.OpenProject(
            FlexLoggerApplication_pb2.OpenProjectRequest(project_path=str(path))
        )
        return Project(self._channel, response.project)

    @classmethod
    def _launch_flexlogger(cls, timeout_in_seconds: int, path: Optional[Path] = None) -> int:
        if path is not None and not path.name.lower().endswith(".exe"):
            path = path / "FlexLogger.exe"
        if path is None:
            path = cls._get_latest_installed_flexlogger_path()
        if path is None:
            raise Exception("Could not determine latest installed path of FlexLogger")
        event_name = uuid.uuid4().hex
        mapped_name = uuid.uuid4().hex

        event = win32event.CreateEvent(None, 0, 0, event_name)
        args = [str(path)]
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
    def _get_latest_installed_flexlogger_path(cls) -> Optional[Path]:
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, _FLEXLOGGER_REGISTRY_KEY_PATH
            ) as flexLoggerKey:
                number_of_subkeys = winreg.QueryInfoKey(flexLoggerKey)[0]
                subkey_names = [winreg.EnumKey(flexLoggerKey, i) for i in range(number_of_subkeys)]
                latest_subkey = sorted([(float(name), name) for name in subkey_names])[-1][1]
                with winreg.OpenKey(flexLoggerKey, latest_subkey) as latest_flexLogger_key:
                    return (
                        Path(winreg.QueryValueEx(latest_flexLogger_key, "Path")[0])
                        / "FlexLogger.exe"
                    )
        except EnvironmentError:
            return None

    @classmethod
    def _read_int_from_mmap(cls, mapped_name: str) -> int:
        with mmap.mmap(-1, 4, tagname=mapped_name, access=mmap.ACCESS_READ) as mapped_file:
            int_bytes = mapped_file.read(4)
            return struct.unpack("i", int_bytes)[0]
