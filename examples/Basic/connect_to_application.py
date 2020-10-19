import sys

from flexlogger.automation import Application


def main() -> int:
    """Connect to an already running instance of FlexLogger with an open project"""
    app = Application()
    project = app.get_active_project()
    test_session_state = project.test_session.state
    print("The test session state is:")
    print(test_session_state)
    print("Press Enter to disconnect from FlexLogger...")
    input()
    app.disconnect()
    return 0


if __name__ == "__main__":
    sys.exit(main())
