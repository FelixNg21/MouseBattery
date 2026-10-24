"""Entry point for the packaged app.

PyInstaller starts from a plain script (it can't use `python -m mousebattery`),
so this file is what gets built. Keep it tiny: the real logic stays in the
mousebattery package.
"""

from mousebattery.logging_setup import setup_logging
from mousebattery.tray import run_tray
from mousebattery.single_instance import SingleInstance
import logging

MUTEX_NAME = "mousebattery"
logger = logging.getLogger("mousebattery.run_tray")

def main() -> int:
    path = setup_logging()
    single_instance = SingleInstance(MUTEX_NAME)
    if not single_instance.acquire():
        logger.info("Another instance holds the lock. Only one instance may run at a time.")
        return 0
    try:
        run_tray()
    finally:
        single_instance.release()


if __name__ == "__main__":
    raise SystemExit(main())
