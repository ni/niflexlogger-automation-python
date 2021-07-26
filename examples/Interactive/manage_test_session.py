import os
import sys
import threading

from consolemenu import ConsoleMenu, Screen
from consolemenu.items import FunctionItem
from flexlogger.automation import Application, TestSessionState


def main(project_path):
    """Interactively manage the state of the FlexLogger project test session.

    Launch FlexLogger, open the specified project and interactively
    manage the state of the FlexLogger project test session.
    """
    print("Launching FlexLogger . . .")
    with Application.launch() as app:
        print("Loading FlexLogger project . . .")
        project = app.open_project(path=project_path)
        test_session = project.test_session

        _show_interactive_menu(test_session)

        print("Closing FlexLogger project . . .")
        project.close()
    return 0


def _start_test(test_session):
    print("Starting test. . . ")
    test_session.start()
    Screen().input("Test started. Press [Enter] to continue")


def _add_note(test_session):
    note = Screen().input("Input the note to log and press [Enter] when the note is complete: ")
    print("Adding note. . . ")
    test_session.add_note(note)
    Screen().input("Note added. Press [Enter] to continue")


def _stop_test(test_session):
    print("Stopping test. . . ")
    test_session.stop()
    Screen().input("Test stopped. Press [Enter] to continue")


def _pause_test(test_session):
    print("Pausing test. . . ")
    test_session.pause()
    Screen().input("Test paused. Press [Enter] to continue")


def _resume_test(test_session):
    print("Resuming test. . . ")
    test_session.resume()
    Screen().input("Test resumed. Press [Enter] to continue")


def _monitor_test_time(test_session):
    print("Monitoring test time. Press [Enter] to stop monitoring. . .")
    thread_exit_event =  threading.Event()
    monitor_test_thread = threading.Thread(target=_monitor_test_time_thread,args=(test_session,thread_exit_event))
    monitor_test_thread.start()
    Screen().input()
    thread_exit_event.set()
    monitor_test_thread.join()


def _monitor_test_time_thread(test_session, exit_event):
    while not exit_event.is_set():
        sys.stdout.write("Elapsed test time: " + str(test_session.elapsed_test_time)),
        sys.stdout.flush()
        sys.stdout.write("\r")


def _show_interactive_menu(test_session):
    """Display an interactive menu based on the current test session state.

    This will return when the user invokes one of the exit menu items.
    """
    # A menu item for all menus, so that test_session.state is checked again
    refresh_test_session_state = FunctionItem(
        "Refresh test session state", _no_op, should_exit=True
    )

    def _create_menu(desc, epilogue_text, menu_items):
        console_menu = ConsoleMenu("Test Session API Demo", desc, epilogue_text=epilogue_text)
        console_menu.append_item(refresh_test_session_state)
        for name, fn, args, opts in menu_items:
            menu_item = FunctionItem(name, fn, args, **opts)
            console_menu.append_item(menu_item)
        return console_menu

    # Set up the command line menus based on the current TestSessionState
    no_channel_to_log_text = (
        "Configure at least one channel that can be logged (such as a DAQ input channel) and then "
        "refresh the test session state. "
    )
    invalid_configuration_text = (
        "Review and address the errors in FlexLogger and then refresh the test session state."
    )
    menus = {
        TestSessionState.IDLE: _create_menu(
            "The test session is idle.",
            "",
            [
                ("Start Test", _start_test, [test_session], {"should_exit": True}),
            ],
        ),
        TestSessionState.RUNNING: _create_menu(
            "The test session is running.",
            "",
            [
                ("Add Note", _add_note, [test_session], {}),
                ("Pause Test", _pause_test, [test_session], {"should_exit": True}),
                ("Stop Test", _stop_test, [test_session], {"should_exit": True}),
                ("Monitor Elapsed Test Time", _monitor_test_time, [test_session], {}),
            ],
        ),
        TestSessionState.PAUSED: _create_menu(
            "The test session is paused.",
            "",
            [
                ("Add Note", _add_note, [test_session], {}),
                ("Resume Test", _resume_test, [test_session], {"should_exit": True}),
                ("Stop Test", _stop_test, [test_session], {"should_exit": True}),
                ("Monitor Elapsed Test Time", _monitor_test_time, [test_session], {}),
            ],
        ),
        TestSessionState.NO_VALID_LOGGED_CHANNELS: _create_menu(
            "The project has no channels to log.", no_channel_to_log_text, []
        ),
        TestSessionState.INVALID_CONFIGURATION: _create_menu(
            "The project has one or more errors.", invalid_configuration_text, []
        ),
    }

    while True:
        state_menu = menus[test_session.state]
        state_menu.show()
        if state_menu.selected_item == state_menu.exit_item:
            break


def _no_op():
    return


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) < 2:
        print("Usage: %s <path of project to open>" % os.path.basename(__file__))
        sys.exit()
    project_path_arg = argv[1]
    sys.exit(main(project_path_arg))
