import pytest

# Remove this line when you start on build_exe.build_args().
pytestmark = pytest.mark.skip(reason="remove this line when you start on build_exe.py")

from build_exe import APP_NAME, ENTRY_POINT, build_args  # noqa: E402

WINDOWLESS_FLAGS = ("--noconsole", "--windowed", "-w")


def test_entry_point_is_the_last_argument():
    assert build_args(debug=False, onefile=False)[-1] == ENTRY_POINT


def test_app_is_named():
    args = build_args(debug=False, onefile=False)
    assert args[args.index("--name") + 1] == APP_NAME


def test_release_build_has_no_console():
    args = build_args(debug=False, onefile=False)
    assert any(flag in args for flag in WINDOWLESS_FLAGS)


def test_debug_build_keeps_the_console():
    args = build_args(debug=True, onefile=False)
    assert not any(flag in args for flag in WINDOWLESS_FLAGS)


def test_onefile_flag_follows_the_option():
    assert "--onefile" in build_args(debug=False, onefile=True)
    assert "--onefile" not in build_args(debug=False, onefile=False)
