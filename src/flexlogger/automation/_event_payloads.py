from ._event_type import EventType
from ._severity_level import SeverityLevel
from .proto import Events_pb2
from datetime import datetime
import json


class EventPayload:
    def __init__(self, event_response: Events_pb2.SubscribeToEventsResponse) -> None:
        self._event_type = EventType.from_event_type_pb2(event_response.event_type)
        self._event_name = event_response.event_name
        self._payload = event_response.payload
        self._timestamp = event_response.timestamp

    @property
    def event_type(self) -> EventType:
        """The type of event received."""
        return self._event_type

    @property
    def event_name(self) -> str:
        """The name of the event received."""
        return self._event_name

    @property
    def timestamp(self) -> datetime:
        """The time the event was received."""
        return self._timestamp


class AlarmPayload(EventPayload):
    def __init__(self, event_response: Events_pb2.SubscribeToEventsResponse) -> None:
        super().__init__(event_response)
        json_payload = json.loads(self._payload)
        self._alarm_id = json_payload['AlarmId']
        self._active = json_payload['Active']
        self._acknowledged = json_payload['Acknowledged']
        self._acknowledged_at = json_payload['AcknowledgedAt']
        self._occurred_at = json_payload['OccurredAt']
        self._severity_level = json_payload['SeverityLevel']
        self._updated_at = json_payload['UpdatedAt']
        self._channel = json_payload['Channel']
        self._condition = json_payload['Condition']
        self._display_name = json_payload['DisplayName']
        self._description = json_payload['Description']

    @property
    def alarm_id(self) -> str:
        """The alarm ID."""
        return self._alarm_id

    @property
    def active(self) -> bool:
        """Whether the alarm is active."""
        return self._active

    @property
    def acknowledged(self) -> bool:
        """Whether the alarm has been acknowledged."""
        return self._acknowledged

    @property
    def acknowledged_at(self) -> datetime:
        """When the alarm was acknowledged."""
        return self._acknowledged_at

    @property
    def occurred_at(self) -> datetime:
        """When the alarm occurred."""
        return self._occurred_at

    @property
    def severity_level(self) -> SeverityLevel:
        """The alarm's severity level."""
        return self._severity_level

    @property
    def updated_at(self) -> datetime:
        """When the alarm was last updated."""
        return self._updated_at

    @property
    def channel(self) -> str:
        """Channel associated with the alarm."""
        return self._channel

    @property
    def condition(self) -> str:
        """The alarm condition."""
        return self._condition

    @property
    def display_name(self) -> str:
        """The alarm's display name."""
        return self._display_name

    @property
    def description(self) -> str:
        """Description of the alarm."""
        return self._description


class FilePayload(EventPayload):
    def __init__(self, event_response: Events_pb2.SubscribeToEventsResponse) -> None:
        super().__init__(event_response)
        self._file_path = self._payload

    @property
    def file_path(self) -> str:
        """The TDMS file path."""
        return self._file_path
