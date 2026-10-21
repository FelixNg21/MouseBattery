from __future__ import annotations

import threading
import time

import pystray

from .display import describe
from .monitor import Monitor
from .reader import open_status_channels
from .render import render_icon

REFRESH_SECONDS = 5

def run_tray() -> None:
    monitor = Monitor(open_status_channels)
    stop = threading.Event()

    def refresh_loop(icon: pystray.Icon) -> None:
        icon.visible = True
        last_key = None
        while not stop.is_set():
            state = monitor.latest()
            status = state.status
            key = (
                status.battery_percent if status else None,
                status.charging if status else False
            )

            if key != last_key: # only redraw when something visible has changed
                icon.icon = render_icon(*key)
                last_key = key

            icon.title = describe(state, time.monotonic())
            stop.wait(REFRESH_SECONDS)

    def quit_app(icon: pystray.Icon, item) -> None:
        stop.set()
        monitor.stop()
        icon.stop()

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
            pystray.MenuItem("Quit", quit_app)
        ),
    )
    monitor.start()
    icon.run(refresh_loop)