import pytest

from mousebattery.startup import StartupError, resolve_exe_path


@pytest.fixture
def fake_exe(tmp_path):
    exe = tmp_path / "MouseBattery.exe"
    exe.write_bytes(b"")
    return exe


def test_explicit_path_wins(fake_exe):
    result = resolve_exe_path(str(fake_exe), frozen=True, executable="ignored.exe")
    assert result == fake_exe.resolve()


def test_frozen_uses_the_running_executable(fake_exe):
    assert resolve_exe_path(None, frozen=True, executable=str(fake_exe)) == fake_exe.resolve()


def test_not_frozen_without_exe_is_an_error():
    with pytest.raises(StartupError, match="--exe"):
        resolve_exe_path(None, frozen=False, executable="python.exe")


def test_missing_file_is_an_error(tmp_path):
    with pytest.raises(StartupError, match="no such file"):
        resolve_exe_path(str(tmp_path / "nope.exe"), frozen=False, executable="python.exe")


def test_non_exe_is_an_error(tmp_path):
    script = tmp_path / "app.py"
    script.write_text("")
    with pytest.raises(StartupError, match=".exe"):
        resolve_exe_path(str(script), frozen=False, executable="python.exe")


def test_result_is_absolute(fake_exe, monkeypatch):
    monkeypatch.chdir(fake_exe.parent)
    assert resolve_exe_path("MouseBattery.exe", frozen=False, executable="x").is_absolute()