from enum import Enum


class TestSessionState(Enum):
    IDLE = 1
    RUNNING = 2
    INVALID_CONFIGURATION = 3
    NO_VALID_LOGGED_CHANNELS = 4
