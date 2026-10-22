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

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "MouseBattery"


def startup_command(exe_path: str) -> str:
    """The command line Windows should run at login.

    TODO: the path may contain spaces ("C:\\Program Files\\..."), and the value is
    parsed like a command line. What does it need so that doesn't break?
    """
    raise NotImplementedError("TODO")


def enable(command: str, key_path: str = RUN_KEY, value_name: str = VALUE_NAME) -> None:
    """Register `command` to run at login.

    TODO: look up winreg.CreateKey / winreg.OpenKey (with KEY_SET_VALUE) and
    winreg.SetValueEx. The key can be passed in so tests can use a throwaway one.
    Which registry type (REG_...) holds a command line?
    """
    raise NotImplementedError("TODO")


def disable(key_path: str = RUN_KEY, value_name: str = VALUE_NAME) -> None:
    """Remove the login entry. Must NOT raise if it was never there (or the key is missing)."""
    raise NotImplementedError("TODO")


def is_enabled(key_path: str = RUN_KEY, value_name: str = VALUE_NAME) -> bool:
    """True if the login entry exists. A missing key or value means False, not an error."""
    raise NotImplementedError("TODO")
