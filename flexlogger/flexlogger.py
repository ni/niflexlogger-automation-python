from typing import Optional
import winreg

_FLEXLOGGER_REGISTRY_KEY_PATH = r"SOFTWARE\National Instruments\FlexLogger"

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

def _launch_flexlogger(path: Optional[str]):
    if path is None:
        path = _get_latest_installed_flexlogger_path()
    if path is None:
        raise Exception("Could not determine latest installed path of FlexLogger")

print(_get_latest_installed_flexlogger_path())