from datetime import timezone
from typing import Callable, List

from grpc import Channel, RpcError

from ._channel_data_point import ChannelDataPoint
from ._flexlogger_error import FlexLoggerError
from .proto import (
    ChannelSpecificationDocument_pb2,
    ChannelSpecificationDocument_pb2_grpc,
)
from .proto.Identifiers_pb2 import ElementIdentifier


class ChannelSpecificationDocument:
    """Represents the document that describes data channels.

    Do not create this class directly; instead, use the return value of
    :meth:`.Project.open_channel_specification_document`.
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

    def get_channel_names(self) -> List[str]:
        """Get all the channel names in the document.

        Raises:
            FlexLoggerError: if getting the channel names fails.
        """
        stub = ChannelSpecificationDocument_pb2_grpc.ChannelSpecificationDocumentStub(self._channel)
        try:
            response = stub.GetChannelNames(
                ChannelSpecificationDocument_pb2.GetChannelNamesRequest(
                    document_identifier=self._identifier
                )
            )
            return response.channel_names
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get channel names") from error

    def get_channel_value(self, channel_name: str) -> ChannelDataPoint:
        """Get the current value of the specified channel.

        Args:
            channel_name: The name of the channel.

        Raises:
            FlexLoggerError: if getting the channel value fails.
        """
        stub = ChannelSpecificationDocument_pb2_grpc.ChannelSpecificationDocumentStub(self._channel)
        try:
            response = stub.GetDoubleChannelValue(
                ChannelSpecificationDocument_pb2.GetDoubleChannelValueRequest(
                    document_identifier=self._identifier, channel_name=channel_name
                )
            )
            # Timestamps come back from FlexLogger in UTC
            return ChannelDataPoint(
                channel_name,
                response.channel_value,
                response.value_timestamp.ToDatetime().replace(tzinfo=timezone.utc),
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get channel value") from error

    def set_channel_value(self, channel_name: str, channel_value: float) -> None:
        """Set the current value of the specified channel.

        Args:
            channel_name: The name of the channel.
            channel_value: The value to set the channel to.

        Raises:
            FlexLoggerError: if setting the channel value fails.
        """
        stub = ChannelSpecificationDocument_pb2_grpc.ChannelSpecificationDocumentStub(self._channel)
        try:
            stub.SetDoubleChannelValue(
                ChannelSpecificationDocument_pb2.SetDoubleChannelValueRequest(
                    document_identifier=self._identifier,
                    channel_name=channel_name,
                    channel_value=channel_value,
                )
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to set channel value") from error
