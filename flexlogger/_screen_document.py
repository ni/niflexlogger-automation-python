from grpc import Channel

from .proto.Identifiers_pb2 import ElementIdentifier


class ScreenDocument:
    """Represents a document that displays data.

    This should not be created directly; instead, the return value of
    :meth:`.Project.open_screen_document` should be used.

    Note that this class currently has no functionality; more functionality
    may be added in the future.
    """

    def __init__(self, channel: Channel, identifier: ElementIdentifier) -> None:
        self._channel = channel
        self._identifier = identifier
