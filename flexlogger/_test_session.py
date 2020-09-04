from flexlogger._test_session_state import TestSessionState
from flexlogger.proto import (
    TestSession_pb2,
    TestSession_pb2_grpc,
)
from flexlogger.proto.TestSessionState_pb2 import TestSessionState as TestSessionState_pb2
from grpc import Channel

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
        stub.AddNote(TestSession_pb2.AddNoteRequest(note=note))

    @property
    def state(self) -> TestSessionState:
        stub = TestSession_pb2_grpc.TestSessionStub(self._channel)
        getTestSessionStateResponse = stub.GetState(TestSession_pb2.GetTestSessionStateRequest())
        state = STATE_MAP.get(getTestSessionStateResponse.test_session_state)
        if state is None:
            raise RuntimeError("The test session is in an undefined state.")
        return state

    def start(self) -> bool:
        stub = TestSession_pb2_grpc.TestSessionStub(self._channel)
        startTestSessionResponse = stub.Start(TestSession_pb2.StartTestSessionRequest())
        return startTestSessionResponse.test_session_started

    def stop(self) -> bool:
        stub = TestSession_pb2_grpc.TestSessionStub(self._channel)
        stopTestSessionResponse = stub.Stop(TestSession_pb2.StopTestSessionRequest())
        return stopTestSessionResponse.test_session_stopped
