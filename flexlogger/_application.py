import mmap
import re
import struct
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any, List, Optional, Union

import grpc  # type: ignore
import win32api  # type: ignore
import win32event  # type: ignore
import winreg  # type: ignore

from ._flexlogger_error import FlexLoggerError
from ._project import Project
from .proto import (
    Application_pb2,  # type: ignore
    Application_pb2_grpc,  # type: ignore
    FlexLoggerApplication_pb2,  # type: ignore
    FlexLoggerApplication_pb2_grpc,  # type: ignore
)

_FLEXLOGGER_REGISTRY_KEY_PATH = r"SOFTWARE\National Instruments\FlexLogger"


class Application:
    def __init__(self, server_port: int) -> None:
        """Connect to an already running instance of FlexLogger

        Args:
            server_port: The port that the automation server is listening to

        """
        self._server_port = server_port
        self._connect()
        self._launched = False

    def __enter__(self) -> "Application":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        # Only exit the application if this was created with Application.launch()
        # If the user wants to override this behavior they can call close()
        # or disconnect() explicitly.
        self._disconnect(exit_application=self._launched)

    @property
    def server_port(self) -> int:
        """Gets the port that the automation server is listening to"""
        return self._server_port

    @classmethod
    def launch(cls, *, timeout: float = 60, path: Union[str, Path] = None) -> "Application":
        """Launches a new instance of FlexLogger.

        Note that if this method is used to initialize a "with" statement, when
        it goes out of scope FlexLogger will be closed.  To prevent this, you can
        explicitly call disconnect() instead.

        Args:
            timeout: How long to wait for FlexLogger to launch before an exception is raised.
                Defaults to 60.
            path: The path to the FlexLogger exe to launch.
                Defaults to None, meaning the latest installed version will be launched.

        Returns:
            The created Application object
        """
        if isinstance(path, str):
            path = Path(path)
        server_port = Application._launch_flexlogger(timeout_in_seconds=timeout, path=path)
        application = Application(server_port=server_port)
        application._launched = True
        return application

    def close(self) -> None:
        """Closes the application and disconnects from the automation server.

        Further calls to this object will fail.
        """
        self._disconnect(exit_application=True)

    def disconnect(self) -> None:
        """Disconnects from the automation server, but leaves the application running.

        Further calls to this object will fail.
        """
        self._disconnect(exit_application=False)

    def _connect(self) -> None:
        if self._server_port <= 0:
            raise ValueError("Tried to connect to invalid port number %d" % self._server_port)
        try:
            self._channel = grpc.insecure_channel("localhost:%d" % self._server_port)
        except grpc.RpcError as error:
            raise FlexLoggerError("Failed to connect to FlexLogger") from error

    def _disconnect(self, exit_application: bool) -> None:
        if self._channel is not None:
            stub = Application_pb2_grpc.ApplicationStub(self._channel)
            stub.Disconnect(Application_pb2.DisconnectRequest(exit_application=exit_application))
            self._channel.close()
            self._channel = None

    def open_project(self, path: Union[str, Path]) -> Project:
        """Opens a project.

        Args:
            path: The path to the project to open.

        Returns:
            The opened project.
        """
        stub = FlexLoggerApplication_pb2_grpc.FlexLoggerApplicationStub(self._channel)
        try:
            response = stub.OpenProject(
                FlexLoggerApplication_pb2.OpenProjectRequest(project_path=str(path))
            )
            return Project(self._channel, response.project)
        except grpc.RpcError as rpc_error:
            raise FlexLoggerError("Failed to close project") from rpc_error

    @classmethod
    def _launch_flexlogger(cls, timeout_in_seconds: float, path: Optional[Path] = None) -> int:
        if path is not None and not path.name.lower().endswith(".exe"):
            path = path / "FlexLogger.exe"
        if path is None:
            path = cls._get_latest_installed_flexlogger_path()
        if path is None:
            raise RuntimeError("Could not determine latest installed path of FlexLogger")
        event_name = uuid.uuid4().hex
        mapped_name = uuid.uuid4().hex

        event = win32event.CreateEvent(None, 0, 0, event_name)
        args = [str(path)]
        args += [
            "-mappedFileIsReadyEventName=" + event_name,
            "-mappedFileName=" + mapped_name,
        ]
        args += ["-enableAutomationServer", "-allowPrototype", "-newProcess"]

        try:
            subprocess.Popen(args)
            timeout_end_time = time.time() + timeout_in_seconds
            while True:
                # Only wait for 200 ms at a time so we can still be responsive to Ctrl-C
                object_signaled = win32event.WaitForSingleObject(event, 200)
                if object_signaled == 0:
                    return cls._read_int_from_mmap(mapped_name)
                elif object_signaled != win32event.WAIT_TIMEOUT:
                    raise RuntimeError(
                        "Internal error waiting for FlexLogger to launch. Error code %d"
                        % object_signaled
                    )
                if time.time() >= timeout_end_time:
                    raise RuntimeError("Timed out waiting for FlexLogger to launch.")
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
                latest_subkey = cls._get_latest_subkey_name(subkey_names)
                if latest_subkey is None:
                    return None
                with winreg.OpenKey(flexLoggerKey, latest_subkey) as latest_flexLogger_key:
                    return (
                        Path(winreg.QueryValueEx(latest_flexLogger_key, "Path")[0])
                        / "FlexLogger.exe"
                    )
        except EnvironmentError:
            return None

    @classmethod
    def _get_latest_subkey_name(cls, names: List[str]) -> Optional[str]:
        """Get the latest version name from the registry key names.

        >>> Application._get_latest_subkey_name(["1.1", "2.0", "7", "foo"])
        '2.0'
        >>> Application._get_latest_subkey_name(["2.100", "2.9", "2.10", "2.1"])
        '2.100'
        >>> Application._get_latest_subkey_name(["9.2", "10.1", "10.0"])
        '10.1'
        >>> Application._get_latest_subkey_name([]) is None
        True
        >>> Application._get_latest_subkey_name(["not real"]) is None
        True
        """
        major_minor_re = re.compile(r"^(\d+)\.(\d+)")
        matches = [major_minor_re.match(name) for name in names]
        sorted_names = sorted(
            (int(match.group(1)), int(match.group(2)), match.group(0))
            for match in matches
            if match is not None
        )
        if len(sorted_names) == 0:
            return None
        return sorted_names[-1][2]

    @classmethod
    def _read_int_from_mmap(cls, mapped_name: str) -> int:
        with mmap.mmap(-1, 4, tagname=mapped_name, access=mmap.ACCESS_READ) as mapped_file:
            int_bytes = mapped_file.read(4)
            return struct.unpack("i", int_bytes)[0]
