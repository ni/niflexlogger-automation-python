class FlexLoggerError(Exception):
    """Represents errors that occur when calling FlexLogger APIs."""

    def __init__(self, message: str) -> None:
        """Initialize an exception.

        Args:
            message: The message describing the error.
        """
        super().__init__(message)
        self._message = message

    @property
    def message(self) -> str:
        """The error message."""
        return self._message
