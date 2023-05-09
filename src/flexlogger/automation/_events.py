import time

from ._event_payloads import AlarmPayload
from ._event_payloads import EventPayload
from ._event_payloads import FilePayload
from ._event_type import EventType
from ._flexlogger_error import FlexLoggerError
from .proto import (
    Events_pb2,
    Events_pb2_grpc,
)
from .proto.EventType_pb2 import EventType as EventType_pb2
from concurrent.futures import ThreadPoolExecutor
from google.protobuf.timestamp_pb2 import Timestamp
from grpc import Channel, RpcError
from typing import Callable, Iterator


class FlexLoggerEventHandler:
    def __init__(self, channel: Channel,
                 client_id: str,
                 application,
                 raise_if_application_closed: Callable[[], None]) -> None:
        self._application = application
        self._callbacks = []
        self._channel = channel
        self._client_id = client_id
        self._event_types_per_callback = []
        self._is_subscribed = False
        self._raise_if_application_closed = raise_if_application_closed
        self._stub = Events_pb2_grpc.FlexLoggerEventsStub(self._channel)
        self._thread_executor = ThreadPoolExecutor()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.unregister_from_events()

    def get_registered_events(self) -> [EventType]:
        """Gets the list of registered event types.

        Returns
            The list of registered event types

        Raises:
            FlexLoggerError: if the request failed.
        """
        try:
            response = self._stub.GetRegisteredEvents(Events_pb2.GetRegisteredEventsRequest(client_id=self._client_id))
            event_types_pb2 = response.event_types
            event_types = self._marshal_event_types_pb2(event_types_pb2)
            return event_types
        except (RpcError, ValueError, AttributeError) as rpc_error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to get the registered events") from rpc_error

    def unregister_from_events(self) -> None:
        """Unregister from events."""
        try:
            self._callbacks = []
            self._event_types_per_callback = []
            self._is_subscribed = False
            self._stub.UnsubscribeFromEvents(Events_pb2.UnsubscribeFromEventsRequest(client_id=self._client_id))
        except (RpcError, ValueError, AttributeError) as rpc_error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to unregister from events") from rpc_error

    def register_event_callback(self, callback, event_types=None) -> None:
        """Register for events and specify a callback method

        Args:
            callback: callback method. The callback method must have the following parameters:
                      application: Application      Reference to the FlexLogger application
                      event_type: EventType         The event type
                      event_payload: EventPayload   The event payload
            event_types: List of EventType to subscribe to.

        Raises:
            FlexLoggerError: if the callback registration failed.
        """
        event_types_parameter = self._marshal_event_types(event_types)
        if self._is_subscribed:
            try:
                self._stub.RegisterEvents(Events_pb2.SubscribeToEventsRequest(client_id=self._client_id,
                                                                              event_types=event_types_parameter))
                self._add_callback_and_events_to_dictionary(callback, event_types)
            except (RpcError, ValueError, AttributeError) as rpc_error:
                self._raise_if_application_closed()
                raise FlexLoggerError("Failed to register events") from rpc_error
            return

        # Add function and event types to respective lists
        self._is_subscribed = True
        self._add_callback_and_events_to_dictionary(callback, event_types)
        event_iterator = self._stub.SubscribeToEvents(
            Events_pb2.SubscribeToEventsRequest(client_id=self._client_id, event_types=event_types_parameter))
        self._thread_executor.submit(self._event_handler, event_iterator)
        # Wait for the server to register the client ID.
        time.sleep(0.15)

    @staticmethod
    def _marshal_event_types(event_types):
        if event_types is None:
            return None
        event_types_pb2 = []
        for event_type in event_types:
            event_types_pb2.append(event_type.to_event_type_pb2())

        return event_types_pb2

    @staticmethod
    def _marshal_event_types_pb2(event_types_pb2):
        if event_types_pb2 is None:
            return None
        event_types = []
        for event_type_pb2 in event_types_pb2:
            event_types.append(EventType.from_event_type_pb2(event_type_pb2))

        return event_types

    def _add_callback_and_events_to_dictionary(self, callback, event_types: [EventType]):
        # If the event type is not provided, respond to all.
        if event_types is None:
            event_types = [EventType.ALARM, EventType.LOG_FILE, EventType.TEST_SESSION, EventType.CUSTOM]

        if callback in self._callbacks:
            index = self._callbacks.index(callback)
            self._event_types_per_callback[index] = event_types
        else:
            self._callbacks.append(callback)
            self._event_types_per_callback.append(event_types)

    def _event_handler(self, event_iterator: Iterator[Events_pb2.SubscribeToEventsResponse]) -> None:
        try:
            while self._is_subscribed:
                event_response = next(event_iterator)
                if event_response is not None:
                    event_type = EventType.from_event_type_pb2(event_response.event_type)
                    for i in range(len(self._callbacks)):
                        if event_type in self._event_types_per_callback[i]:
                            payload = self._create_payload(event_response)
                            self._callbacks[i](self._application, event_type, payload)
        except Exception as error:
            self._raise_if_application_closed()
            raise FlexLoggerError("Failed to receive event.") from error

    @staticmethod
    def _create_payload(event_response: Events_pb2.SubscribeToEventsResponse):
        if event_response.event_type == EventType_pb2.EVENT_TYPE_ALARM:
            payload = AlarmPayload(event_response)
        elif event_response.event_type == EventType_pb2.EVENT_TYPE_LOG_FILE:
            payload = FilePayload(event_response)
        else:
            payload = EventPayload(event_response)

        return payload
