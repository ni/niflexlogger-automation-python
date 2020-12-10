import re
from typing import cast

from grpc import RpcError


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
        message = self._message
        if isinstance(self.__cause__, RpcError):
            cause = cast(RpcError, self.__cause__)
            search_result = re.search(r"\(([^)]+)", cause.details())
            inner_details = search_result.group(1)  # type: ignore
            if len(inner_details) >= 0:
                message += ". Additional error details: " + inner_details

        return message

    def __repr__(self) -> str:
        return f"FlexLoggerError({repr(self.message)})"

    def __str__(self) -> str:
        return self.message
