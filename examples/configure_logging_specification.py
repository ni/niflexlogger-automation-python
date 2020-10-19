import os
import sys
from typing import Any, List

from consolemenu import ConsoleMenu, Screen
from consolemenu.items import FunctionItem
from flexlogger.automation import (
    Application,
    FlexLoggerError,
    LoggingSpecificationDocument,
    TestSession,
    TestSessionState,
)
from prettytable import PrettyTable


def main(argv: List[str] = None) -> int:
    """Interactively configure the FlexLogger logging specification.

    Launch FlexLogger, open the specified project and interactively
    configuring the FlexLogger logging specification.
    """
    if argv is None:
        argv = sys.argv
    if len(argv) < 2:
        print("Usage: %s <path of project to open>" % os.path.basename(__file__))
        return 1

    project_path = argv[1]
    print("Launching FlexLogger . . .")
    with Application.launch() as app:
        print("Loading FlexLogger project . . .")
        project = app.open_project(path=project_path)
        test_session = project.test_session
        logging_specification_document = project.open_logging_specification_document()

        _show_interactive_menu(test_session, logging_specification_document)

        print("Closing FlexLogger project . . .")
        project.close()
    return 0


def _show_interactive_menu(
    test_session: TestSession, logging_specification_document: LoggingSpecificationDocument
) -> None:
    """Display an interactive menu for configuring the logging specification.

    Some configuration options are not available if the test session is running.

    This will return when the user invokes one of the exit menu items.
    """
    # A menu item for all menus, so that test_session.state is checked again
    refresh_test_session_state = FunctionItem(
        "Refresh test session state", _no_op, should_exit=True
    )

    def _create_menu(desc: str, epilogue_text: str, menu_items: List[Any]) -> ConsoleMenu:
        console_menu = ConsoleMenu(
            "Logging Specification Document API Demo", desc, epilogue_text=epilogue_text
        )
        console_menu.append_item(refresh_test_session_state)
        for name, fn, args, opts in menu_items:
            menu_item = FunctionItem(name, fn, args, **opts)
            console_menu.append_item(menu_item)
        return console_menu

    edits_allowed_menu = _create_menu(
        "The test session is currently idle.",
        "",
        [
            ("Show the log file path", _show_log_file_path, [logging_specification_document], {}),
            ("Set the log file path", _set_log_file_path, [logging_specification_document], {}),
            (
                "Show all test properties",
                _show_test_properties,
                [logging_specification_document],
                {},
            ),
            ("Show a test property", _show_test_property, [logging_specification_document], {}),
            ("Set a test property", _set_test_property, [logging_specification_document], {}),
            (
                "Remove a test property",
                _remove_test_property,
                [logging_specification_document],
                {},
            ),
        ],
    )
    edits_not_allowed_menu = _create_menu(
        "The test session is currently running.",
        "",
        [
            ("Show the log file path", _show_log_file_path, [logging_specification_document], {}),
            (
                "Show all test properties",
                _show_test_properties,
                [logging_specification_document],
                {},
            ),
            ("Show a test property", _show_test_property, [logging_specification_document], {}),
        ],
    )

    while True:
        # Edits to the logging specification are not allowed while the test is running
        state = test_session.state
        if state == TestSessionState.RUNNING:
            active_menu = edits_not_allowed_menu
        elif state == TestSessionState.IDLE:
            edits_allowed_menu.subtitle = "The test session is currently idle."
            active_menu = edits_allowed_menu
        elif state == TestSessionState.NO_VALID_LOGGED_CHANNELS:
            edits_allowed_menu.subtitle = "The project has no channels to log."
            active_menu = edits_allowed_menu
        else:
            edits_allowed_menu.subtitle = "The project has one or more errors."
            active_menu = edits_allowed_menu
        active_menu.show()
        if active_menu.selected_item == active_menu.exit_item:
            break


def _show_log_file_path(logging_specification_document: LoggingSpecificationDocument) -> None:
    log_file_base_path = logging_specification_document.get_log_file_base_path()
    print("The log file base path is: " + log_file_base_path)
    if "{" in log_file_base_path:
        resolved_log_file_base_path = (
            logging_specification_document.get_resolved_log_file_base_path()
        )
        print("The resolved log file base path is: " + resolved_log_file_base_path)
    log_file_name = logging_specification_document.get_log_file_name()
    print("The log file name is: " + log_file_name)
    if "{" in log_file_name:
        resolved_log_file_name = logging_specification_document.get_resolved_log_file_name()
        print("The resolved log file file name is: " + resolved_log_file_name)
    Screen().input("Press [Enter] to continue")


def _set_log_file_path(logging_specification_document: LoggingSpecificationDocument) -> None:
    log_file_base_path = Screen().input("Input the log file base path and press [Enter]: ")
    log_file_name = Screen().input("Input the log file name and [Enter]: ")
    logging_specification_document.set_log_file_base_path(log_file_base_path)
    logging_specification_document.set_log_file_name(log_file_name)
    Screen().input("Log file path updated. Press [Enter] to continue")


def _show_test_properties(logging_specification_document: LoggingSpecificationDocument) -> None:
    test_properties = logging_specification_document.get_test_properties()
    table = PrettyTable(["Name", "Value", "Prompt on start"])
    for test_property in test_properties:
        table.add_row([test_property.name, test_property.value, test_property.prompt_on_start])
    print(table)
    Screen().input("Press [Enter] to continue")


def _show_test_property(logging_specification_document: LoggingSpecificationDocument) -> None:
    test_property_name = Screen().input(
        "Input the name of the test property to show and press [Enter]: "
    )
    try:
        test_property = logging_specification_document.get_test_property(test_property_name)
        print("The test property name is: " + test_property.name)
        print("The test property value is: " + test_property.value)
        if test_property.prompt_on_start:
            print("The user will be prompted to set the value of this property on test start.")
        else:
            print("The user will not be prompted to set the value of this property on test start.")
        Screen().input("Press [Enter] to continue")
    except FlexLoggerError:
        Screen().input(
            'Test property could not be retrieved, possibly because no test property is named "'
            + test_property_name
            + '". Press [Enter] to continue'
        )


def _set_test_property(logging_specification_document: LoggingSpecificationDocument) -> None:
    property_name = Screen().input(
        "Input the name of the test property to create or modify and press [Enter]: "
    )
    property_value = Screen().input("Input the value for the test property and press [Enter]: ")
    prompt_on_start_input = (
        Screen()
        .input(
            "Input if the user should be prompted to set the value of this "
            "property on test start (y|n) and press [Enter]: "
        )
        .lower()
        .strip()
    )
    if prompt_on_start_input[0] == "y":
        prompt_on_start = True
    else:
        prompt_on_start = False
    logging_specification_document.set_test_property(property_name, property_value, prompt_on_start)
    Screen().input("Test property set. Press [Enter] to continue")


def _remove_test_property(logging_specification_document: LoggingSpecificationDocument) -> None:
    test_property_name = Screen().input(
        "Input the name of the test property to remove and press [Enter]: "
    )
    try:
        logging_specification_document.remove_test_property(test_property_name)
        Screen().input("Test property removed. Press [Enter] to continue")
    except FlexLoggerError:
        Screen().input(
            'Test property could not be removed, possibly because no test property is named "'
            + test_property_name
            + '". Press [Enter] to continue'
        )


def _no_op() -> None:
    return


if __name__ == "__main__":
    sys.exit(main())
