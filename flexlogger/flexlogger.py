from typing import Optional
import mmap
import struct
import subprocess
import uuid
# TODO - install this with requirements.txt or pyproject.toml or something to install pywin32
import win32api
import win32event
import winreg

_FLEXLOGGER_REGISTRY_KEY_PATH = r"SOFTWARE\National Instruments\FlexLogger"

# TODO - need to make this parameter actually optional
def _launch_flexlogger(path: Optional[str]):
    if path is None:
        path = _get_latest_installed_flexlogger_path()
    if path is None:
        raise Exception("Could not determine latest installed path of FlexLogger")
    event_name = uuid.uuid4().hex
    mapped_name = uuid.uuid4().hex

    event = win32event.CreateEvent(None, 0, 0, event_name)
    args = [path]
    args += ["-mappedFileIsReadyEventName=" + event_name, "-mappedFileName=" + mapped_name]
    args += ["-enableAutomationServer", "-allowPrototype"]
    # TODO - close if client closes option
    print(args)
    server_port = None
    try:
        print("Launching...")
        subprocess.Popen(args)
        # TODO - configurable timeout here? Or just something reasonable?
        TIMEOUT_IN_SECONDS = 60
        launched = False
        for i in range(TIMEOUT_IN_SECONDS):
            object_signaled = win32event.WaitForSingleObject(event, 1000)
            if object_signaled == 0:
                print("Launched!")
                launched = True
                server_port = _read_int_from_mmap(mapped_name)
                print("server_port is %d" % (server_port))
                break
            elif object_signaled != 258:
                print("Something went wrong: " + str(object_signaled))
                break
        if not launched:
            print("Timed out")
    finally:
        win32api.CloseHandle(event)

def _get_latest_installed_flexlogger_path() -> Optional[str]:
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, _FLEXLOGGER_REGISTRY_KEY_PATH) as flexLoggerKey:
            number_of_subkeys = winreg.QueryInfoKey(flexLoggerKey)[0]
            subkey_names = [winreg.EnumKey(flexLoggerKey, i) for i in range(number_of_subkeys)]
            latest_subkey = sorted([(float(name), name) for name in subkey_names])[-1][1]
            with winreg.OpenKey(flexLoggerKey, latest_subkey) as latest_flexLogger_key:
                return winreg.QueryValueEx(latest_flexLogger_key, "Path")[0]
    except:
        return None

def _read_int_from_mmap(mapped_name: str) -> int:
    with mmap.mmap(-1, 4, tagname=mapped_name, access=mmap.ACCESS_READ) as mapped_file:
        int_bytes = mapped_file.read(4)
        return struct.unpack('i', int_bytes)[0]

print(_get_latest_installed_flexlogger_path())
_launch_flexlogger(path=None)