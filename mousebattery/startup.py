"""Start the app when you log in to Windows, using the per-user "Run" registry key.

Why the registry and not a Startup-folder shortcut: writing a .lnk file needs COM
(pywin32) or PowerShell, while `winreg` is in the standard library. Making the
shortcut version instead is a good stretch exercise.

The key lives at HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
and holds one string value per program: name -> command line.

`winreg` only exists on Windows, so import it INSIDE the functions. That keeps this
module importable (and startup_command() testable) on any platform.
"""

from __future__ import annotations
from pathlib import Path

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "MouseBattery"

class StartupError(Exception):
    """The login entry can't be set up (ex. a bad exe path)."""

def resolve_exe_path(explicit: str | None, frozen: bool, executable: str) -> Path:
    """Determine which exe should be started at login."""
    if explicit: path = Path(explicit)
    elif frozen: path = Path(executable)
    else: raise StartupError(
        "not running from a built exe. pass it's location with --exe"
    )

    path = path.resolve()
    if path.suffix.lower() != ".exe":
        raise StartupError(f"expected an .exe file, got: {path}")
    if not path.is_file():
        raise StartupError(f"no such file: {path}")
    return path

def startup_command(exe_path: str) -> str:
    """The command line Windows should run at login.
    """
    return f'"{exe_path}"'


def enable(command: str, key_path: str = RUN_KEY, value_name: str = VALUE_NAME) -> None:
    """Register `command` to run at login.
    """
    import winreg

    handle = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
    winreg.SetValueEx(handle, value_name, 0, winreg.REG_SZ, command)


def disable(key_path: str = RUN_KEY, value_name: str = VALUE_NAME) -> None:
    """Remove the login entry. Must NOT raise if it was never there (or the key is missing)."""
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, value_name)
    except FileNotFoundError:
        pass


def is_enabled(key_path: str = RUN_KEY, value_name: str = VALUE_NAME) -> bool:
    """True if the login entry exists. A missing key or value means False, not an error."""
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.QueryValueEx(key, value_name)
    except FileNotFoundError:
        return False
    return True