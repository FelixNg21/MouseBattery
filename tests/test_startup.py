import sys

import pytest

from mousebattery.startup import (  # noqa: E402
    VALUE_NAME,
    disable,
    enable,
    is_enabled,
    startup_command,
)

windows_only = pytest.mark.skipif(sys.platform != "win32", reason="needs the Windows registry")

TEST_KEY = r"Software\mousebattery-tests"


def test_command_is_quoted_so_spaces_survive():
    path = r"C:\Program Files\MouseBattery\MouseBattery.exe"
    assert startup_command(path) == '"' + path + '"'


@pytest.fixture
def throwaway_key():
    """A scratch registry key, so tests never touch the real Run key."""
    yield TEST_KEY
    import winreg

    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, TEST_KEY)
    except FileNotFoundError:
        pass


@windows_only
def test_not_enabled_when_the_key_does_not_exist_yet(throwaway_key):
    assert not is_enabled(key_path=throwaway_key)


@windows_only
def test_enable_then_is_enabled(throwaway_key):
    enable(r'"C:\app.exe"', key_path=throwaway_key)
    assert is_enabled(key_path=throwaway_key)


@windows_only
def test_enable_stores_the_command(throwaway_key):
    import winreg

    enable(r'"C:\app.exe"', key_path=throwaway_key)
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, throwaway_key) as key:
        value, _kind = winreg.QueryValueEx(key, VALUE_NAME)
    assert value == r'"C:\app.exe"'


@windows_only
def test_disable_removes_the_entry(throwaway_key):
    enable(r'"C:\app.exe"', key_path=throwaway_key)
    disable(key_path=throwaway_key)
    assert not is_enabled(key_path=throwaway_key)


@windows_only
def test_disable_when_never_enabled_is_harmless(throwaway_key):
    disable(key_path=throwaway_key)  # must not raise

@windows_only
def test_disable_leaves_other_entries_alone(throwaway_key):
    import winreg

    enable(r'"C:\app.exe"', key_path=throwaway_key)
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, throwaway_key) as key:
        winreg.SetValueEx(key, "SomeOtherApp", 0, winreg.REG_SZ, r'"C:\other.exe"')

    disable(key_path=throwaway_key)

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, throwaway_key) as key:
        value, _kind = winreg.QueryValueEx(key, "SomeOtherApp")
    assert value == r'"C:\other.exe"'