from __future__ import annotations

import logging
import threading
import time
import os
import sys

import pystray

from .display import describe
from .monitor import Monitor
from .reader import open_status_channels
from .render import render_icon
from .logging_setup import log_path
from .startup import is_enabled, disable, enable, resolve_exe_path, startup_command

REFRESH_SECONDS = 5
logger = logging.getLogger(__name__)

def run_tray() -> None:
    monitor = Monitor(open_status_channels)
    stop = threading.Event()

    def refresh_loop(icon: pystray.Icon) -> None:
        icon.visible = True
        last_key = None
        while not stop.is_set():
            try:
                state = monitor.latest()
                status = state.status
                key = (
                    status.battery_percent if status else None,
                    status.charging if status else False,
                )
                if key != last_key:  # only redraw when something visible changed
                    icon.icon = render_icon(*key)
                    last_key = key
                icon.title = describe(state, time.monotonic())
            except Exception:
                logger.exception("tray refresh failed")
            stop.wait(REFRESH_SECONDS)

    def open_log(icon: pystray.Icon, item) -> None:
        try:
            os.startfile(log_path())  # Windows only
        except (AttributeError, OSError):
            logger.warning("could not open log file", exc_info=True)

    def quit_app(icon: pystray.Icon, item) -> None:
        logger.info("quit requested")
        stop.set()
        monitor.stop()
        icon.stop()

    def toggle_startup(icon: pystray.Icon, item) -> None:
        try:
            if is_enabled():
                disable()
                logger.info("start at login: disabled")
            else:
                exe = resolve_exe_path(None, getattr(sys, "frozen", False), sys.executable)
                enable(startup_command(str(exe)))
                logger.info("start at login: enabled (%s)", exe)
        except Exception:
            logger.exception("could not change the start-at-login setting")
        icon.update_menu()

    icon = pystray.Icon(
        "Mousebattery",
        render_icon(None, False),
        "Starting...",
        menu = pystray.Menu(
            pystray.MenuItem(
                lambda item: describe(monitor.latest(), time.monotonic()),
                None,
                enabled=False
            ),
            pystray.MenuItem("Open log file", open_log),
            pystray.MenuItem("Start at login", toggle_startup, checked=lambda item: is_enabled(), enabled=getattr(sys, "frozen", False)),
            pystray.MenuItem("Quit", quit_app)
        ),
    )
    logger.info("tray started")
    monitor.start()
    icon.run(refresh_loop)