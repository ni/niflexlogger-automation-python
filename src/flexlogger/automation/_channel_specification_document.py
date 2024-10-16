from datetime import timezone
from typing import Callable, List

from grpc import Channel, RpcError

from ._channel_data_point import ChannelDataPoint
from ._data_rate_level import DataRateLevel
from ._flexlogger_error import FlexLoggerError
from .proto import (
    ChannelSpecificationDocument_pb2,
    ChannelSpecificationDocument_pb2_grpc,
)
from .proto.Identifiers_pb2 import ElementIdentifier
from .proto.DataRateLevel_pb2 import DataRateLevel as DataRateLevel_pb2

DATA_RATE_LEVEL_MAP = {
    DataRateLevel.SLOW: DataRateLevel_pb2.DATA_RATE_LEVEL_SLOW,
    DataRateLevel.MEDIUM: DataRateLevel_pb2.DATA_RATE_LEVEL_MEDIUM,
    DataRateLevel.FAST: DataRateLevel_pb2.DATA_RATE_LEVEL_FAST,
    DataRateLevel.COUNTER: DataRateLevel_pb2.DATA_RATE_LEVEL_COUNTER,
    DataRateLevel.DIGITAL: DataRateLevel_pb2.DATA_RATE_LEVEL_DIGITAL,
    DataRateLevel.ON_DEMAND: DataRateLevel_pb2.DATA_RATE_LEVEL_ON_DEMAND,
}

DATA_RATE_LEVEL_PB2_MAP = {
    DataRateLevel_pb2.DATA_RATE_LEVEL_SLOW: DataRateLevel.SLOW,
    DataRateLevel_pb2.DATA_RATE_LEVEL_MEDIUM: DataRateLevel.MEDIUM,
    DataRateLevel_pb2.DATA_RATE_LEVEL_FAST: DataRateLevel.FAST,
    DataRateLevel_pb2.DATA_RATE_LEVEL_COUNTER: DataRateLevel.COUNTER,
    DataRateLevel_pb2.DATA_RATE_LEVEL_DIGITAL: DataRateLevel.DIGITAL,
    DataRateLevel_pb2.DATA_RATE_LEVEL_ON_DEMAND: DataRateLevel.ON_DEMAND,
}


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

    def get_actual_data_rate(self, channel_name: str) -> float:
        """Get the actual data rate for the specified channel.

        Args:
            channel_name: The name of the channel.
        """
        stub = ChannelSpecificationDocument_pb2_grpc.ChannelSpecificationDocumentStub(self._channel)
        try:
            response = stub.GetActualDataRate(
                ChannelSpecificationDocument_pb2.GetActualDataRateRequest(
                    document_identifier=self._identifier,  channel_name=channel_name
                )
            )

            return response.data_rate
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get the actual data rate.") from error

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

    def get_data_rate(self, data_rate_level: DataRateLevel) -> float:
        """Get the data rate for a specific date rate level in Hertz.

        Args:
            data_rate_level: The data rate level to get the data rate for.

        Raises:
            FlexLoggerError: if the data_rate_level is invalid.
        """
        stub = ChannelSpecificationDocument_pb2_grpc.ChannelSpecificationDocumentStub(self._channel)
        try:
            data_rate_level_parameter = DATA_RATE_LEVEL_MAP.get(data_rate_level)
            response = stub.GetDataRate(
                ChannelSpecificationDocument_pb2.GetDataRateRequest(
                    document_identifier=self._identifier, data_rate_level=data_rate_level_parameter
                )
            )

            return response.data_rate
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get the data rate: data rate level invalid.") from error

    def get_data_rate_level(self, channel_name: str) -> DataRateLevel:
        """Get the data rate level of the specified channel

        Args:
            channel_name: The name of the channel.

        Raises:
            FlexLoggerError: if getting the data rate level fails.
        """
        stub = ChannelSpecificationDocument_pb2_grpc.ChannelSpecificationDocumentStub(self._channel)
        try:
            response = stub.GetDataRateLevel(
                ChannelSpecificationDocument_pb2.GetDataRateLevelRequest(
                    document_identifier=self._identifier, channel_name=channel_name
                )
            )

            return DATA_RATE_LEVEL_PB2_MAP.get(response.data_rate_level)
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get the data rate level.") from error

    def is_channel_enabled(self, channel_name: str) -> bool:
        """Get the current enabled state of the specified channel.

        Args:
            channel_name: The name of the channel.

        Raises:
            FlexLoggerError: if getting the channel value fails.
        """
        stub = ChannelSpecificationDocument_pb2_grpc.ChannelSpecificationDocumentStub(self._channel)
        try:
            response = stub.IsChannelEnabled(
                ChannelSpecificationDocument_pb2.IsChannelEnabledRequest(
                    document_identifier=self._identifier, channel_name=channel_name
                )
            )

            return response.channel_enabled
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get channel enable state") from error

    def set_channel_enabled(self, channel_name: str, channel_enabled: bool) -> None:
        """Enable or disable the specified channel.

        Args:
            channel_name: The name of the channel.
            channel_enabled: The channel enabled state: true to enable the channel, false to disable it.

        Raises:
            FlexLoggerError: if enabling or disabling the channel fails.
        """
        stub = ChannelSpecificationDocument_pb2_grpc.ChannelSpecificationDocumentStub(self._channel)
        try:
            stub.SetChannelEnabled(
                ChannelSpecificationDocument_pb2.SetChannelEnabledRequest(
                    document_identifier=self._identifier,
                    channel_name=channel_name,
                    channel_enabled=channel_enabled,
                )
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to set the channel enable state") from error

    def is_channel_logging_enabled(self, channel_name: str) -> bool:
        """Get the current logging state of the specified channel.

        Args:
            channel_name: The name of the channel.

        Raises:
            FlexLoggerError: if getting the channel value fails.
        """
        stub = ChannelSpecificationDocument_pb2_grpc.ChannelSpecificationDocumentStub(self._channel)
        try:
            response = stub.IsChannelLoggingEnabled(
                ChannelSpecificationDocument_pb2.IsChannelLoggingEnabledRequest(
                    document_identifier=self._identifier, channel_name=channel_name
                )
            )

            return response.channel_logging_enabled
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get channel logging enable state") from error

    def set_channel_logging_enabled(self, channel_name: str, channel_logging_enabled: bool) -> None:
        """Enable or disable logging for the specified channel.

        Args:
            channel_name: The name of the channel.
            channel_logging_enabled: The channel logging enabled state: true to enable logging, false to disable it.

        Raises:
            FlexLoggerError: if enabling or disabling the channel logging fails.
        """
        stub = ChannelSpecificationDocument_pb2_grpc.ChannelSpecificationDocumentStub(self._channel)
        try:
            stub.SetChannelLoggingEnabled(
                ChannelSpecificationDocument_pb2.SetChannelLoggingEnabledRequest(
                    document_identifier=self._identifier,
                    channel_name=channel_name,
                    channel_logging_enabled=channel_logging_enabled,
                )
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to set the channel logging state") from error

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

    def set_data_rate(self, data_rate_level: DataRateLevel, data_rate: float) -> None:
        """Set the data rate of a specific data rate level.

        Args:
            data_rate_level: The data rate level to get the data rate for.
            data_rate: The value of the data rate to set in Hertz.

        Raises:
            FlexLoggerError: if setting the data rate fails.
        """
        stub = ChannelSpecificationDocument_pb2_grpc.ChannelSpecificationDocumentStub(self._channel)
        try:
            data_rate_level_parameter = DATA_RATE_LEVEL_MAP.get(data_rate_level)
            stub.SetDataRate(
                ChannelSpecificationDocument_pb2.SetDataRateRequest(
                    document_identifier=self._identifier,
                    data_rate_level=data_rate_level_parameter,
                    data_rate=data_rate
                )
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to set the data rate") from error

    def set_data_rate_level(self, channel_name: str, data_rate_level: DataRateLevel) -> None:
        """Set the data rate level of the specified channel
           Note: This may affect other channels in the same module or chassis set to the same data rate level.

        Args:
            channel_name: The name of the channel.
            data_rate_level: The data rate level to set.

        Raises:
            FlexLoggerError: if setting the data rate level fails.
        """
        stub = ChannelSpecificationDocument_pb2_grpc.ChannelSpecificationDocumentStub(self._channel)
        try:
            data_rate_level_parameter = DATA_RATE_LEVEL_MAP.get(data_rate_level)
            stub.SetDataRateLevel(
                ChannelSpecificationDocument_pb2.SetDataRateLevelRequest(
                    document_identifier=self._identifier,
                    channel_name=channel_name,
                    data_rate_level=data_rate_level_parameter
                )
            )
        except (RpcError, ValueError) as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to set the data rate level.") from error
