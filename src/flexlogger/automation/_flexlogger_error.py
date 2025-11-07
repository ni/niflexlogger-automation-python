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
        inner_details = self._get_inner_details()
        if len(inner_details) == 0:
            return self._message

        inner_details = re.sub(r"\[([0-9+-]+)\] ", "", inner_details)
        return self._message + ". Additional error details: " + inner_details

    @property
    def error_code(self) -> int:
        """The error code."""
        inner_details = self._get_inner_details()
        if len(inner_details) == 0:
            return 0

        error_code_result = re.search(r"\[([0-9+-]+)\] ", inner_details)
        return int(error_code_result.group(1)) if error_code_result else 0

    def __repr__(self) -> str:
        return f"FlexLoggerError({repr(self.message)})"

    def __str__(self) -> str:
        return self.message

    def _get_inner_details(self) -> str:
        if not isinstance(self.__cause__, RpcError):
            return ""

        cause = cast(RpcError, self.__cause__)
        return cause.details()
