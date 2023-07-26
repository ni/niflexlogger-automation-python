import mmap
import os
import re
import struct
import subprocess
import sys
import time
import uuid
from pathlib import Path
from socket import SOCK_STREAM
from typing import Any, List, Optional, Union

# Do not import anything from win32api here (instead, import them in the
# methods they're needed in). Linux machines need to be able to import our
# module so buildthedocs will be able to use automodule correctly to generate
# our API Reference documentation.
import psutil  # type: ignore
from grpc import insecure_channel, RpcError

from ._events import FlexLoggerEventHandler
from ._flexlogger_error import FlexLoggerError
from ._project import Project
from .proto import (
    Application_pb2,  # type: ignore
    Application_pb2_grpc,  # type: ignore
    FlexLoggerApplication_pb2,  # type: ignore
    FlexLoggerApplication_pb2_grpc,  # type: ignore
)

_FLEXLOGGER_REGISTRY_KEY_PATH = r"SOFTWARE\National Instruments\FlexLogger"
_FLEXLOGGER_EXE_NAME = "FlexLogger.exe"
_FLEXLOGGER_PORT_FILE_PATH = Path(r"National Instruments\FlexLogger\LastAutomationPort.txt")
_APP_CLOSE_TIMEOUT = 60


class Application:
    """Represents the FlexLogger application."""

    def __init__(self, server_port: int = None) -> None:
        """Connect to an already running instance of FlexLogger.

        Args:
            server_port: The port that the automation server is listening to.  Omit this
                argument or pass None to detect the port of a running FlexLogger automatically.

        Raises:
            FlexLoggerError: if connecting fails.
        """
        Application._raise_if_unsupported_platform()
        self._server_port = server_port if server_port is not None else self._detect_server_port()
        self._connect()
        self._launched = False
        self._event_handler = None
        self._client_id = uuid.uuid4().hex

    def __enter__(self) -> "Application":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        # Only exit the application if this was created with Application.launch()
        # If the user wants to override this behavior they can call close()
        # or disconnect() explicitly.
        self._disconnect(exit_application=self._launched)

    @property
    def event_handler(self) -> FlexLoggerEventHandler:
        """The application event handler."""
        if self._event_handler is not None:
            return self._event_handler

        self._event_handler = FlexLoggerEventHandler(self._channel,
                                                     self._client_id,
                                                     self,
                                                     self._raise_exception_if_closed)
        return self._event_handler

    @property
    def server_port(self) -> int:
        """The port that the automation server is listening to."""
        return self._server_port

    @classmethod
    def launch(cls, *, timeout: float = 40, path: Union[str, Path] = None) -> "Application":
        """Launch a new instance of FlexLogger.

        Note that if this method is used to initialize a "with" statement, when
        the Application goes out of scope FlexLogger will be closed.  To prevent this,
        call :meth:`~.Application.disconnect()`.

        Args:
            timeout: The length of time, in seconds, to wait for FlexLogger to launch
                before raising an exception.
                Defaults to 40.
            path: The path to the FlexLogger executable to launch.
                Defaults to None, meaning the latest installed version will be launched.

        Returns:
            The created Application object

        Raises:
            FlexLoggerError: if launching FlexLogger or connecting to it fails.
        """
        Application._raise_if_unsupported_platform()
        if isinstance(path, str):
            path = Path(path)
        server_port = Application._launch_flexlogger(timeout_in_seconds=timeout, path=path)
        application = Application(server_port=server_port)
        application._launched = True
        return application

    def close(self) -> None:
        """Close the application and disconnect from the automation server.

        Further calls to this object will fail.
        """
        self._disconnect(exit_application=True)

    def disconnect(self) -> None:
        """Disconnect from the automation server, but leave the application running.

        Further calls to this object will fail.
        """
        self._disconnect(exit_application=False)

    @classmethod
    def _raise_if_unsupported_platform(cls) -> None:
        if sys.maxsize != 2 ** 63 - 1:
            raise FlexLoggerError("This API only supports 64-bit versions of Python.")

    def _connect(self) -> None:
        if self._server_port <= 0:
            raise ValueError("Tried to connect to invalid port number %d" % self._server_port)
        try:
            self._channel = insecure_channel("localhost:%d" % self._server_port)
        except RpcError as error:
            raise FlexLoggerError(
                'Failed to connect to FlexLogger. Ensure the "Automation server" preference is '
                "enabled in the application. "
            ) from error

    def _disconnect(self, exit_application: bool) -> None:
        if self._channel is not None:
            stub = Application_pb2_grpc.ApplicationStub(self._channel)
            pid_to_wait_for = None
            if exit_application:
                # Find the application that's using this port
                pid_candidates = set(
                    x.pid
                    for x in psutil.net_connections()
                    if x.type == SOCK_STREAM
                    and x.laddr[1] == self._server_port
                    and x.pid != os.getpid()
                )
                for pid in pid_candidates:
                    if psutil.Process(pid).name().lower() == _FLEXLOGGER_EXE_NAME.lower():
                        pid_to_wait_for = pid
                        break
            try:
                if exit_application:
                    # If there is an active project, close it so closing the
                    # app won't prompt to save it.
                    active_project = self.get_active_project()
                    if active_project is not None:
                        active_project.close()
                stub.Disconnect(
                    Application_pb2.DisconnectRequest(exit_application=exit_application)
                )
                if pid_to_wait_for is not None:
                    # Wait 60 seconds for the process to exit
                    timeout_end_time = time.time() + _APP_CLOSE_TIMEOUT
                    process_still_running = True
                    while time.time() < timeout_end_time and process_still_running:
                        # Only wait for 200 ms at a time so we can still be responsive to Ctrl-C
                        time.sleep(0.2)
                        try:
                            # This will raise an exception if the process doesn't exist.
                            # But it's also possible the PID has been reused, so see if
                            # the name is the same.
                            process_still_running = (
                                psutil.Process(pid_to_wait_for).name().lower()
                                == _FLEXLOGGER_EXE_NAME.lower()
                            )
                        except psutil.Error:
                            process_still_running = False
            except (RpcError, ValueError, AttributeError) as rpc_error:
                self._raise_exception_if_closed()
                raise FlexLoggerError("Failed to disconnect") from rpc_error
            finally:
                self._channel.close()
                self._channel = None
                self._event_handler = None

    def _raise_exception_if_closed(self) -> None:
        if self._channel is None:
            raise FlexLoggerError("Application has already been disconnected") from None

    def open_project(self, path: Union[str, Path]) -> Project:
        """Open a project.

        Args:
            path: The path to the project you want to open.

        Returns:
            The opened project.

        Raises:
            FlexLoggerError: if opening the project fails.
        """
        try:
            stub = FlexLoggerApplication_pb2_grpc.FlexLoggerApplicationStub(self._channel)
            response = stub.OpenProject(
                FlexLoggerApplication_pb2.OpenProjectRequest(project_path=str(path))
            )
            # FlexLogger can hang if you open and then immediately close a project,
            # this seems sufficient to prevent that.
            time.sleep(1.0)
            return Project(self._channel, self._raise_exception_if_closed, response.project)
        # For most methods, catching ValueError is sufficient to detect whether the Application
        # has been closed, and avoids race conditions where another thread closes the Application
        # in the middle of the first thread's call.
        #
        # This method passes self._channel directly to a stub, and this raises an AttributeError
        # if self._channel is None, so catch this as well.
        except (RpcError, ValueError, AttributeError) as rpc_error:
            self._raise_exception_if_closed()
            raise FlexLoggerError("Failed to open project") from rpc_error

    def get_active_project(self) -> Optional[Project]:
        """Gets the currently active (open) project.

        Returns:
            The active project, or None if a project is not currently open.

        Raises:
            FlexLoggerError: if getting the active project fails.
        """
        try:
            stub = FlexLoggerApplication_pb2_grpc.FlexLoggerApplicationStub(self._channel)
            response = stub.GetActiveProject(FlexLoggerApplication_pb2.GetActiveProjectRequest())
            if response.active_project_available:
                return Project(self._channel, self._raise_exception_if_closed, response.project)
            else:
                return None
        # For most methods, catching ValueError is sufficient to detect whether the Application
        # has been closed, and avoids race conditions where another thread closes the Application
        # in the middle of the first thread's call.
        #
        # This method passes self._channel directly to a stub, and this raises an AttributeError
        # if self._channel is None, so catch this as well.
        except (RpcError, ValueError, AttributeError) as rpc_error:
            self._raise_exception_if_closed()
            raise FlexLoggerError("Failed to get the active project") from rpc_error

    @classmethod
    def _launch_flexlogger(cls, timeout_in_seconds: float, path: Optional[Path] = None) -> int:
        import win32api  # type: ignore
        import win32event  # type: ignore

        if path is not None and not path.name.lower().endswith(".exe"):
            path = path / _FLEXLOGGER_EXE_NAME
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
        args += ["-enableAutomationServer"]

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
                    raise RuntimeError(
                        "Timed out waiting for FlexLogger to launch.  This might mean an "
                        "instance of FlexLogger was already running."
                    )
        finally:
            win32api.CloseHandle(event)

    @classmethod
    def _get_server_port_file_path(cls) -> Path:
        from win32com.shell import shell, shellcon  # type: ignore

        program_data_path = Path(shell.SHGetFolderPath(0, shellcon.CSIDL_COMMON_APPDATA, 0, 0))
        return program_data_path / _FLEXLOGGER_PORT_FILE_PATH

    def _detect_server_port(self) -> int:
        """Detect the server_port of a running FlexLogger."""
        port_file_path = Application._get_server_port_file_path()
        if not port_file_path.exists():
            raise RuntimeError(
                "No running FlexLogger detected.  If FlexLogger is running, this might mean the "
                "automation server is not enabled.  To turn on the automation server, see the "
                "General tab of the Preferences in FlexLogger."
            )
        try:
            with open(str(port_file_path), "r") as f:
                text = f.read().strip()
                return int(text)
        except Exception as ex:
            raise RuntimeError("Failed to read automation port from running FlexLogger.") from ex

    @classmethod
    def _get_latest_installed_flexlogger_path(cls) -> Optional[Path]:
        import winreg  # type: ignore

        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, _FLEXLOGGER_REGISTRY_KEY_PATH
            ) as flexLoggerKey:
                number_of_subkeys = winreg.QueryInfoKey(flexLoggerKey)[0]
                subkey_names = [winreg.EnumKey(flexLoggerKey, i) for i in range(number_of_subkeys)]
                # Try the newer "CurrentVerison" subkey first,
                # then the older version specific subkeys
                subkey = cls._get_current_version_subkey_name(subkey_names)
                if subkey is None:
                    subkey = cls._get_latest_subkey_name(subkey_names)
                    if subkey is None:
                        return None
                with winreg.OpenKey(flexLoggerKey, subkey) as latest_flexLogger_key:
                    return (
                        Path(winreg.QueryValueEx(latest_flexLogger_key, "Path")[0])
                        / _FLEXLOGGER_EXE_NAME
                    )
        except EnvironmentError:
            return None

    @classmethod
    def _get_current_version_subkey_name(cls, names: List[str]) -> Optional[str]:
        if "CurrentVersion" in names:
            return "CurrentVersion"
        else:
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
