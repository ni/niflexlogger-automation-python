class TestProperty:
    """Information about a test property."""

    def __init__(self, property_name: str, property_value: str, prompt_on_start: bool):
        """Create a new TestProperty.

        Args:
            property_name: The name of the property.
            property_value: The value of the property.
            prompt_on_start: Whether the operator should be prompted to define this
                property when the test session starts.
        """
        self._property_name = property_name
        self._property_value = property_value
        self._prompt_on_start = prompt_on_start

    @property
    def property_name(self) -> str:
        """The name of the property."""
        return self._property_name

    @property
    def property_value(self) -> str:
        """The value of the property."""
        return self._property_value

    @property
    def prompt_on_start(self) -> bool:
        """Whether this property should be set when the test session starts.

        If this is set to true, the operator should be prompted to define this property
        when the test session starts.
        """
        return self._prompt_on_start
