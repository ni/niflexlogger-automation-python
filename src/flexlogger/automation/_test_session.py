from typing import Callable

from grpc import Channel, RpcError

from ._flexlogger_error import FlexLoggerError
from ._test_session_state import TestSessionState
from .proto import (
    TestSession_pb2,
    TestSession_pb2_grpc,
)
from .proto.TestSessionState_pb2 import TestSessionState as TestSessionState_pb2

STATE_MAP = {
    TestSessionState_pb2.TEST_SESSION_STATE_IDLE: TestSessionState.IDLE,
    TestSessionState_pb2.TEST_SESSION_STATE_RUNNING: TestSessionState.RUNNING,
    TestSessionState_pb2.TEST_SESSION_STATE_INVALID_CONFIGURATION: (
        TestSessionState.INVALID_CONFIGURATION
    ),
    TestSessionState_pb2.TEST_SESSION_STATE_NO_VALID_LOGGED_CHANNELS: (
        TestSessionState.NO_VALID_LOGGED_CHANNELS
    ),
}


class TestSession:
    """Represents a test session for a project.

    Do not create this class directly; instead, use the property
    :attr:`.Project.test_session`.
    """

    def __init__(self, channel: Channel, raise_if_application_closed: Callable[[], None]) -> None:
        self._channel = channel
        self._raise_if_application_closed = raise_if_application_closed

    def add_note(self, note: str) -> None:
        """Add a note to the current log file.

        This method requires the test session to be in the
        :attr:`.TestSessionState.RUNNING` state.

        Args:
            note: The note to add to the log file.

        Raises:
            FlexLoggerError: if the test session is not in the
                :attr:`.TestSessionState.RUNNING` state, or if adding the note fails.
        """
        stub = TestSession_pb2_grpc.TestSessionStub(self._channel)
        try:
            stub.AddNote(TestSession_pb2.AddNoteRequest(note=note))
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to add note") from error

    @property
    def state(self) -> TestSessionState:
        """Get the current state of the test session.

        Raises:
            FlexLoggerError: if getting the current state fails.
        """
        self._raise_if_application_closed()
        stub = TestSession_pb2_grpc.TestSessionStub(self._channel)
        try:
            getTestSessionStateResponse = stub.GetState(
                TestSession_pb2.GetTestSessionStateRequest()
            )
            state = STATE_MAP.get(getTestSessionStateResponse.test_session_state)
            if state is None:
                raise RuntimeError("The test session is in an undefined state.")
            return state
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get test session state") from error

    def start(self) -> bool:
        """Start the test session, if possible.

        Returns:
            True if the test was started, otherwise False.

        Raises:
            FlexLoggerError: if starting the test session fails.
        """
        stub = TestSession_pb2_grpc.TestSessionStub(self._channel)
        try:
            startTestSessionResponse = stub.Start(TestSession_pb2.StartTestSessionRequest())
            return startTestSessionResponse.test_session_started
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to start test session") from error

    def stop(self) -> bool:
        """Stop the test session, if possible.

        Returns:
            True if the test was stopped, otherwise False.

        Raises:
            FlexLoggerError: if stopping the test session fails.
        """
        stub = TestSession_pb2_grpc.TestSessionStub(self._channel)
        try:
            stopTestSessionResponse = stub.Stop(TestSession_pb2.StopTestSessionRequest())
            return stopTestSessionResponse.test_session_stopped
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to stop test session") from error
