class FlexLoggerError(Exception):
    def __init__(self, message: str) -> None:
        self._message = message

    @property
    def message(self) -> str:
        return self._message
