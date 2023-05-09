from flexlogger.automation import AlarmPayload
from flexlogger.automation import Application
from flexlogger.automation import EventPayload
from flexlogger.automation import EventType
from flexlogger.automation import FilePayload
import os
import sys


def main(project_path):
    """Launch FlexLogger, open a project, and wait for an event."""
    with Application.launch() as app:
        project = app.open_project(path=project_path)

        # Get a reference to the event handler and register callback functions for different event types.
        event_handler = app.event_handler
        event_handler.register_event_callback(alarms_event_handler, [EventType.ALARM])
        event_handler.register_event_callback(log_file_event_handler, [EventType.LOG_FILE])
        event_handler.register_event_callback(session_event_handler, [EventType.TEST_SESSION])

        test_session = project.test_session
        test_session.start()
        print("Test started. Press Enter to stop the test and close the project...")

        # Wait for the user to press enter
        input()

        # Cleanup: stop the session, close the project and unregister from the events
        test_session.stop()
        project.close()
        event_handler.unregister_from_events()

    return 0


def alarms_event_handler(application: Application, event_type: EventType, payload: AlarmPayload):
    """Alarm Event Handler
    This method will be called when an alarm event is fired.

    Args:
        application: Application    Reference to the application, so that you can access the project, session, etc
        event_type: EventType       The event type
        payload: AlarmPayload       The event payload
    """

    print("Event of type: {}, received at {}".format(event_type, payload.timestamp))
    print("Event Name: {}".format(payload.event_name))
    print("Alarm occurred on channel: {}".format(payload.channel))
    print("Alarm Severity Level: {}".format(payload.severity_level))

    # Stop the session when the alarm is received
    project = application.get_active_project()
    session = project.test_session
    session.stop()


def log_file_event_handler(application: Application, event_type: EventType, payload: FilePayload):
    """FlexLogger Event Handler
    This method will be called when a file event is fired.

        Args:
            application: Application    Reference to the application, so that you can access the project, session, etc
            event_type: EventType       The event type
            payload: FilePayload        The event payload
    """

    print("Event of type: {}, received at {}".format(event_type, payload.timestamp))
    print("Event Name: {}".format(payload.event_name))
    print("TDMS file path: {}".format(payload.file_path))


def session_event_handler(application: Application, event_type: EventType, payload: EventPayload):
    """FlexLogger Event Handler
    This method will be called when a session event is fired.

    Args:
        application: Application    Reference to the application, so that you can access the project, session, etc
        event_type: EventType       The event type
        payload: EventPayload       The event payload
    """

    print("Event of type: {}, received at {}".format(event_type, payload.timestamp))
    print("Event Name: {}".format(payload.event_name))


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) < 2:
        print("Usage: %s <path of project to open>" % os.path.basename(__file__))
        sys.exit()
    project_path_arg = argv[1]
    sys.exit(main(project_path_arg))
