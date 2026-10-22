"""Entry point for the packaged app.

PyInstaller starts from a plain script (it can't use `python -m mousebattery`),
so this file is what gets built. Keep it tiny: the real logic stays in the
mousebattery package.
"""

from mousebattery.logging_setup import setup_logging
from mousebattery.tray import run_tray


def main() -> int:
    # TODO 1: set up logging first, so even startup failures get recorded.
    path = setup_logging()
    # TODO 2: (after you've written single_instance.py) exit quietly if another
    #         copy of the app is already running.
    # TODO 3: run the tray.
    run_tray()
    # raise NotImplementedError("TODO: write main()")


if __name__ == "__main__":
    raise SystemExit(main())
