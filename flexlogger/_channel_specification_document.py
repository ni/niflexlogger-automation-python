from typing import List

from grpc import Channel, RpcError

from ._double_channel_data_point import DoubleChannelDataPoint
from ._flexlogger_error import FlexLoggerError
from .proto import (
    ChannelSpecificationDocument_pb2,
    ChannelSpecificationDocument_pb2_grpc,
)
from .proto.Identifiers_pb2 import ElementIdentifier


class ChannelSpecificationDocument:
    def __init__(self, channel: Channel, identifier: ElementIdentifier) -> None:
        self._channel = channel
        self._identifier = identifier

    def get_channel_names(self) -> List[str]:
        """Get all the channel names in the document."""
        stub = ChannelSpecificationDocument_pb2_grpc.ChannelSpecificationDocumentStub(self._channel)
        try:
            response = stub.GetChannelNames(
                ChannelSpecificationDocument_pb2.GetChannelNamesRequest(
                    document_identifier=self._identifier
                )
            )
            return response.channel_names
        except RpcError as rpc_error:
            raise FlexLoggerError("Failed to get channel names") from rpc_error

    def get_double_channel_value(self, channel_name: str) -> DoubleChannelDataPoint:
        """Get the current value of the specified channel.

        Args:
            channel_name: The name of the channel to get the current value of
        """
        stub = ChannelSpecificationDocument_pb2_grpc.ChannelSpecificationDocumentStub(self._channel)
        try:
            response = stub.GetDoubleChannelValue(
                ChannelSpecificationDocument_pb2.GetDoubleChannelValueRequest(
                    document_identifier=self._identifier, channel_name=channel_name
                )
            )
            return DoubleChannelDataPoint(
                channel_name, response.channel_value, response.value_timestamp.ToDatetime()
            )
        except RpcError as rpc_error:
            raise FlexLoggerError("Failed to get double channel value") from rpc_error

    def set_double_channel_value(self, channel_name: str, channel_value: float) -> None:
        """Set the current value of the specified channel.

        Args:
            channel_name: The name of the channel to set the current value of
            channel_value: The value to set the channel to
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
        except RpcError as rpc_error:
            raise FlexLoggerError("Failed to set double channel value") from rpc_error
