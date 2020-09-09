from flexlogger._flexlogger_error import FlexLoggerError
from flexlogger._test_session_state import TestSessionState
from flexlogger.proto import (
    TestSession_pb2,
    TestSession_pb2_grpc,
)
from flexlogger.proto.TestSessionState_pb2 import TestSessionState as TestSessionState_pb2
from grpc import Channel, RpcError

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
    def __init__(self, channel: Channel) -> None:
        self._channel = channel

    def add_note(self, note: str) -> None:
        stub = TestSession_pb2_grpc.TestSessionStub(self._channel)
        try:
            stub.AddNote(TestSession_pb2.AddNoteRequest(note=note))
        except RpcError as rpc_error:
            raise FlexLoggerError("Failed to add note") from rpc_error

    @property
    def state(self) -> TestSessionState:
        stub = TestSession_pb2_grpc.TestSessionStub(self._channel)
        try:
            getTestSessionStateResponse = stub.GetState(
                TestSession_pb2.GetTestSessionStateRequest()
            )
            state = STATE_MAP.get(getTestSessionStateResponse.test_session_state)
            if state is None:
                raise RuntimeError("The test session is in an undefined state.")
            return state
        except RpcError as rpc_error:
            raise FlexLoggerError("Failed to get test session state") from rpc_error

    def start(self) -> bool:
        stub = TestSession_pb2_grpc.TestSessionStub(self._channel)
        try:
            startTestSessionResponse = stub.Start(TestSession_pb2.StartTestSessionRequest())
            return startTestSessionResponse.test_session_started
        except RpcError as rpc_error:
            raise FlexLoggerError("Failed to start test session") from rpc_error

    def stop(self) -> bool:
        stub = TestSession_pb2_grpc.TestSessionStub(self._channel)
        try:
            stopTestSessionResponse = stub.Stop(TestSession_pb2.StopTestSessionRequest())
            return stopTestSessionResponse.test_session_stopped
        except RpcError as rpc_error:
            raise FlexLoggerError("Failed to stop test session") from rpc_error
