import pytest

from mousebattery import startup
from mousebattery.cli import main


@pytest.fixture
def fake_exe(tmp_path):
    exe = tmp_path / "MouseBattery.exe"
    exe.write_bytes(b"")
    return exe


def test_install_registers_the_quoted_path(monkeypatch, fake_exe, capsys):
    registered = []
    monkeypatch.setattr(startup, "enable", lambda command, **kw: registered.append(command))
    assert main(["install-startup", "--exe", str(fake_exe)]) == 0
    assert registered == [f'"{fake_exe.resolve()}"']
    assert "Registered" in capsys.readouterr().out


def test_install_from_source_without_exe_fails(monkeypatch, capsys):
    monkeypatch.setattr(startup, "enable", lambda *a, **kw: pytest.fail("must not register"))
    assert main(["install-startup"]) == 1
    assert "--exe" in capsys.readouterr().err


def test_uninstall_when_not_registered(monkeypatch, capsys):
    monkeypatch.setattr(startup, "is_enabled", lambda **kw: False)
    monkeypatch.setattr(startup, "disable", lambda **kw: pytest.fail("nothing to remove"))
    assert main(["uninstall-startup"]) == 0
    assert "Nothing to remove" in capsys.readouterr().out


def test_uninstall_removes_the_entry(monkeypatch, capsys):
    removed = []
    monkeypatch.setattr(startup, "is_enabled", lambda **kw: True)
    monkeypatch.setattr(startup, "disable", lambda **kw: removed.append(True))
    assert main(["uninstall-startup"]) == 0
    assert removed
    assert "Removed" in capsys.readouterr().out