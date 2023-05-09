from .utils import open_project
import datetime
from flexlogger.automation import (
    Application,
    EventPayload,
    EventNames,
    EventType
)
import pytest  # type: ignore

received_event_type = None
received_event_payload = None


def generic_event_handler(application: Application, event_type: EventType, payload: EventPayload):
    """Event Handler
    This method will be called when a file event is fired.

    Args:
        application: Application    Reference to the application, so that you can access the project, session, etc
        event_type: EventType       The event type
        payload: EventPayload       The event payload
    """
    global received_event_type
    global received_event_payload

    received_event_type = event_type
    received_event_payload = payload
    print("Event received: {}".format(event_type))


class TestEvents:
    @staticmethod
    def wait_for_registered_events(event_handler, timeout=3) -> [EventType]:
        start_time = datetime.datetime.now()
        while True:
            registered_events = event_handler.get_registered_events()
            current_time = datetime.datetime.now()
            delta = current_time - start_time
            if len(registered_events) > 0 or delta.total_seconds() > timeout:
                break

        return registered_events

    @staticmethod
    def wait_for_event(event_type=None, event_name=None, timeout=5) -> bool:
        global received_event_type
        global received_event_payload

        start_time = datetime.datetime.now()
        while True:
            correct_event_type = received_event_type == event_type if event_type is not None else True
            if event_name is not None:
                correct_event_name = False if received_event_payload is None else received_event_payload.event_name == event_name
            else:
                correct_event_name = True

            current_time = datetime.datetime.now()
            delta = current_time - start_time
            if (correct_event_type and correct_event_name) or delta.total_seconds() > timeout:
                break

        return correct_event_type and correct_event_name

    @staticmethod
    def reset_event() -> [None]:
        global received_event_type
        global received_event_payload
        received_event_type = None
        received_event_payload = None

    @pytest.mark.integration  # type: ignore
    def test__register_events__events_registered(self, app: Application) -> None:
        self.reset_event()
        event_handler = app.event_handler
        event_handler.register_event_callback(generic_event_handler, [EventType.ALARM])
        registered_events = self.wait_for_registered_events(event_handler)
        assert EventType.ALARM in registered_events
        assert event_handler._is_subscribed
        event_handler.unregister_from_events()

    @pytest.mark.integration  # type: ignore
    def test__unregister_events__no_events_registered(self, app: Application) -> None:
        self.reset_event()
        event_handler = app.event_handler
        event_handler.register_event_callback(generic_event_handler, [EventType.ALARM])
        event_handler.unregister_from_events()
        registered_events = self.wait_for_registered_events(event_handler)
        assert len(registered_events) == 0
        assert not event_handler._is_subscribed
        event_handler.unregister_from_events()

    @pytest.mark.integration  # type: ignore
    def test__start_session__session_event_received(self, app: Application) -> None:
        self.reset_event()
        with open_project(app, "ProjectWithProducedData") as project:
            event_handler = app.event_handler
            event_handler.register_event_callback(generic_event_handler, [EventType.TEST_SESSION])
            session = project.test_session
            session.start()
            event_received = self.wait_for_event(EventType.TEST_SESSION, EventNames.TEST_STARTED)
            assert event_received
            event_handler.unregister_from_events()

    @pytest.mark.integration  # type: ignore
    def test__start_session__log_file_created_event_received(self, app: Application) -> None:
        self.reset_event()
        with open_project(app, "ProjectWithProducedData") as project:
            event_handler = app.event_handler
            event_handler.register_event_callback(generic_event_handler, [EventType.LOG_FILE])
            session = project.test_session
            session.start()
            event_received = self.wait_for_event(EventType.LOG_FILE, EventNames.LOG_FILE_CREATED)
            assert event_received
            event_handler.unregister_from_events()

    @pytest.mark.integration  # type: ignore
    def test__stop_session__session_event_received(self, app: Application) -> None:
        self.reset_event()
        with open_project(app, "ProjectWithProducedData") as project:
            event_handler = app.event_handler
            event_handler.register_event_callback(generic_event_handler, [EventType.TEST_SESSION])
            session = project.test_session
            session.start()
            session.stop()
            event_received = self.wait_for_event(EventType.TEST_SESSION, EventNames.TEST_STOPPED)
            assert event_received
            event_handler.unregister_from_events()

    @pytest.mark.integration  # type: ignore
    def test__stop_session__log_file_closed_event_received(self, app: Application) -> None:
        self.reset_event()
        with open_project(app, "ProjectWithProducedData") as project:
            event_handler = app.event_handler
            event_handler.register_event_callback(generic_event_handler, [EventType.LOG_FILE])
            session = project.test_session
            session.start()
            session.stop()
            event_received = self.wait_for_event(EventType.LOG_FILE, EventNames.LOG_FILE_CLOSED)
            assert event_received
            event_handler.unregister_from_events()

    @pytest.mark.integration  # type: ignore
    def test_open_project_with_alarms__start_session__alarm_event_received(self, app: Application) -> None:
        self.reset_event()
        with open_project(app, "ProjectWithAlarms") as project:
            event_handler = app.event_handler
            event_handler.register_event_callback(generic_event_handler, [EventType.ALARM])
            session = project.test_session
            session.start()
            event_received = self.wait_for_event(EventType.ALARM)
            assert event_received
            event_handler.unregister_from_events()
