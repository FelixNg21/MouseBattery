"""Build the app with PyInstaller.

Usage:
    python build_exe.py --debug      # keeps a console window; use this first
    python build_exe.py              # windowless folder build
    python build_exe.py --onefile    # single .exe
"""

from __future__ import annotations

import argparse

APP_NAME = "MouseBattery"
ENTRY_POINT = "run_tray.py"


def build_args(debug: bool, onefile: bool) -> list[str]:
    """Return the PyInstaller command-line arguments, as a list of strings.

    TODO: write this. Look up these in the PyInstaller docs ("Options"):
      --name            what the .exe is called (use APP_NAME)
      --onedir/--onefile  folder of files vs. one self-extracting .exe
      --noconsole       no terminal window (but NOT for a --debug build)
      --noconfirm, --clean   so rebuilding doesn't ask questions or reuse stale files
      --hidden-import   modules PyInstaller can't see because they're imported
                        dynamically (pystray chooses its backend at runtime!)
    The entry point must be the last argument.
    """
    raise NotImplementedError("TODO: write build_args()")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=f"Build {APP_NAME} with PyInstaller")
    parser.add_argument("--debug", action="store_true", help="keep the console window")
    parser.add_argument("--onefile", action="store_true", help="single .exe instead of a folder")
    args = parser.parse_args(argv)

    # Imported here so build_args() can be tested without PyInstaller installed.
    import PyInstaller.__main__

    PyInstaller.__main__.run(build_args(debug=args.debug, onefile=args.onefile))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
