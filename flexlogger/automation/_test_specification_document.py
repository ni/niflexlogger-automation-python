from typing import Callable

from grpc import Channel

from .proto.Identifiers_pb2 import ElementIdentifier


class TestSpecificationDocument:
    """Represents a document that describes a test.

    This should not be created directly; instead, the return value of
    :meth:`.Project.open_test_specification_document` should be used.

    Note that this class currently has no functionality; more functionality
    may be added in the future.
    """

    def __init__(
        self,
        channel: Channel,
        raise_if_application_closed: Callable[[], None],
        identifier: ElementIdentifier,
    ) -> None:
        self._channel = channel
        self._raise_if_application_closed = raise_if_application_closed
        self._identifier = identifier
