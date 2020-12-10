class TestProperty:
    """Information about a test property."""

    def __init__(self, name: str, value: str, prompt_on_start: bool):
        """Create a new TestProperty.

        Args:
            name: The name of the property.
            value: The value of the property.
            prompt_on_start: Whether the operator should be prompted to define this
                property when the test session starts.
        """
        self._name = name
        self._value = value
        self._prompt_on_start = prompt_on_start

    def __repr__(self) -> str:
        return 'flexlogger.automation.TestProperty("%s", "%s", %s)' % (
            self._name,
            self._value,
            str(self._prompt_on_start),
        )

    @property
    def name(self) -> str:
        """The name of the property."""
        return self._name

    @property
    def value(self) -> str:
        """The value of the property."""
        return self._value

    @property
    def prompt_on_start(self) -> bool:
        """Whether this property should be set when the test session starts.

        If this is set to true, the operator should be prompted to define this property
        when the test session starts.
        """
        return self._prompt_on_start
