import os
import sys
import time
import csv
from flexlogger.automation import Application, FlexLoggerError, TestSessionState


def test_sequence1(config_file_path):
    """Launch FlexLogger, reference the CSV file,
    open the specified FlexLogger projects,
    and control a simulated DUT.

    The CSV lists the path to the FlexLogger projects,
    DUT commands, and test times.

    To use this example with your DUT or other external hardware,
    replace the 'dut_control' function with your specific DUT's API
    or communication methods, as needed.
    """
    print("\nLaunching FlexLogger...")
    with Application.launch() as app:
        print("FlexLogger Launched Successfully!\n")
        dut_control("powerOn")
        dut_control("updateFirmware")
        test1(app, config_file_path)
        dut_control("powerOff")
    print("FlexLogger Closed Successfully")
    return


def test1(app_reference, config_path):
    with open(config_path, newline="") as csvfile:
        csvdata = csv.reader(csvfile)
        next(csvdata)  # skip header
        for row in csvdata:
            [
                proj_path,
                state0,
                time0,
                state1,
                time1,
                state2,
                time2,
                state3,
                time3,
            ] = row
            if not os.path.isabs(proj_path):
                config_root_dir = os.path.dirname(config_path)
                proj_path = os.path.normpath(os.path.join(config_root_dir, proj_path))
            print("Loading Project...")
            try:
                project = app_reference.open_project(proj_path)
            except FlexLoggerError as upstream_error:
                if not os.path.isfile(proj_path):
                    raise FileNotFoundError(
                        "\n\nCheck CSV file. Cannot find FlexLogger project at path:\n{}".format(
                            proj_path
                        )
                    ) from upstream_error
                else:
                    raise
            print("Project Loaded\n")
            test_session = project.test_session
            print("\nStarting Test...")
            start_test(test_session)
            print("Test Started\n")
            dut_control("changeState", state0)
            display_elapsed_test_time(time0, test_session)
            dut_control("changeState", state1)
            display_elapsed_test_time(time1, test_session)
            print("Pause Test")
            test_session.pause()
            dut_control("changeState", state2)
            time.sleep(5)
            print("Resume Test")
            test_session.resume()
            display_elapsed_test_time(time2, test_session)
            dut_control("changeState", state3)
            display_elapsed_test_time(time3, test_session)
            test_session.stop()
            print("Test Completed.\n\nClosing Project...")
            project.close()
            print("Project Closed\n")
    return


def start_test(
    test_session, retries=3
):  # This is a workaround for the FlexLogger API .start() method bug
    for retry in range(retries):
        test_session.start()
        if test_session.state == TestSessionState.RUNNING:
            return
        elif retry < retries - 1:
            print("Waiting for test session to start. Retry: {}".format(retry + 1))
            time.sleep(1)
            continue
        else:
            raise RuntimeError("Test did not start within timeout.")


def dut_control(command, state="error"):
    if command == "powerOn":
        print("DUT Powered ON\n")
    elif command == "powerOff":
        print("DUT Powered OFF\n")
    elif command == "changeState":
        print("Change DUT to State " + str(state))
    elif command == "updateFirmware":
        print("Simulate Downloading DUT Firmware...")
        time.sleep(2)
        print("DUT Firmware Downloaded Successfully\n")
    else:
        print("Error: Incorrect DUT Command\n")
    return


def display_elapsed_test_time(total_time, test_session):
    elapsed_time_at_start = test_session.elapsed_test_time
    time_diff = 0
    total_time_float = float(total_time)
    while time_diff < total_time_float:
        time.sleep(0.1)
        time_diff = (test_session.elapsed_test_time - elapsed_time_at_start).total_seconds()
        print("Test Case Time: {} seconds".format(format(time_diff, ".3f")), end="\r")
    print("Test Case Time: {} seconds".format(format(time_diff, ".3f")), end="\n\n")
    return


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) < 2:
        print("Usage: %s <path to CSV file>" % os.path.basename(__file__))
        sys.exit()
    config_file_path = argv[1]
    sys.exit(test_sequence1(config_file_path))
