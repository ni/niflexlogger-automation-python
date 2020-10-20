import sys

from flexlogger.automation import Application


def main():
    """Connect to an already running instance of FlexLogger with an open project"""
    app = Application()
    project = app.get_active_project()
    if project is None:
        print("No project is open in FlexLogger!")
        return 1
    test_session_state = project.test_session.state
    print("The test session state is:")
    print(test_session_state)
    print("Press Enter to disconnect from FlexLogger...")
    input()
    app.disconnect()
    return 0


if __name__ == "__main__":
    sys.exit(main())
