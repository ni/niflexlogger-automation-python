from enum import Enum


class TestSessionState(Enum):
    """An enumeration describing the possible states of a :class:`.TestSession`."""

    IDLE = 1
    """The :class:`.TestSession` is idle and not running.

    Configuration changes can occur during this state.
    """

    RUNNING = 2
    """The :class:`.TestSession` is logging.

    Configuration changes are not allowed during this state.
    """

    INVALID_CONFIGURATION = 3
    """The project has a configuration error."""

    NO_VALID_LOGGED_CHANNELS = 4
    """No channels have been configured, or all channels are disabled or not available."""
