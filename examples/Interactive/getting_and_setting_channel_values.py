import os
import sys

from consolemenu import ConsoleMenu, Screen
from consolemenu.items import FunctionItem
from flexlogger.automation import (
    Application,
    FlexLoggerError,
)
from prettytable import PrettyTable


def main(project_path):
    """Interactively get and set FlexLogger channel values.

    Launch FlexLogger, open the specified project and interactively
    get and set FlexLogger channel values.
    """
    print("Launching FlexLogger . . .")
    with Application.launch() as app:
        print("Loading FlexLogger project . . .")
        project = app.open_project(path=project_path)
        channel_specification_document = project.open_channel_specification_document()

        _show_interactive_menu(channel_specification_document)

        print("Closing FlexLogger project . . .")
        project.close()
    return 0


def _show_channel_values(channel_specification_document):
    channel_names = channel_specification_document.get_channel_names()
    table = PrettyTable(["Channel name", "Value", "Timestamp"])
    for channel_name in channel_names:
        try:
            channel_data_point = channel_specification_document.get_channel_value(channel_name)
            table.add_row(
                [
                    channel_data_point.name,
                    channel_data_point.value,
                    # Convert the timestamp from UTC to local time
                    channel_data_point.timestamp.astimezone(None),
                ]
            )
        except FlexLoggerError:
            # Getting a channel that is not available, configured or enabled will raise
            # an exception. Ignore those exceptions and continue to the next channel.
            pass
    print(table)
    Screen().input("Press [Enter] to continue")


def _set_channel_value(channel_specification_document):
    channel_name = Screen().input("Input the name of the channel to set and press [Enter]: ")
    channel_value = Screen().input("Input the value for the channel and press [Enter]: ")
    try:
        channel_specification_document.set_channel_value(channel_name, float(channel_value))
        Screen().input("Channel value set. Press [Enter] to continue")
    except FlexLoggerError:
        Screen().input(
            'Channel value could not be set, possibly because no channel is named "'
            + channel_name
            + '". Press [Enter] to continue'
        )
    except ValueError:
        Screen().input(
            "A value of "
            + channel_value
            + " could not be set on "
            + channel_name
            + " because it could not be converted to a floating point value."
            + " Press [Enter] to continue"
        )


def _show_interactive_menu(channel_specification_document):
    """Display an interactive menu for getting and setting channel values.

    This will return when the user invokes the exit menu item.
    """

    def _create_menu(desc, epilogue_text, menu_items):
        console_menu = ConsoleMenu(
            "Getting and Setting Channel Values API Demo", desc, epilogue_text=epilogue_text
        )
        for name, fn, args, opts in menu_items:
            menu_item = FunctionItem(name, fn, args, **opts)
            console_menu.append_item(menu_item)
        return console_menu

    get_set_channel_values_menu = _create_menu(
        "",
        "",
        [
            ("Show all channel values", _show_channel_values, [channel_specification_document], {}),
            ("Set a channel value", _set_channel_value, [channel_specification_document], {}),
        ],
    )

    while True:
        get_set_channel_values_menu.show()
        if get_set_channel_values_menu.selected_item == get_set_channel_values_menu.exit_item:
            break


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) < 2:
        print("Usage: %s <path of project to open>" % os.path.basename(__file__))
        sys.exit()
    project_path_arg = argv[1]
    sys.exit(main(project_path_arg))
