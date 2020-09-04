from grpc import Channel

from .proto.Identifiers_pb2 import ElementIdentifier


class TestSpecificationDocument:
    def __init__(self, channel: Channel, identifier: ElementIdentifier) -> None:
        self._channel = channel
        self._identifier = identifier
