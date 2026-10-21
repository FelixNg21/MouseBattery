from __future__ import annotations

import threading
import time
from contextlib import AbstractContextManager
from dataclasses import dataclass, replace
from typing import Callable

from .reader import PacketSource, read_status_from
from .status import StatusReport

@dataclass(frozen=True)
class MonitorState:
    status: StatusReport | None = None
    updated_at: float | None = None
    connected: bool = False
    error: str | None = None

Connect = Callable[[], AbstractContextManager[list[PacketSource]]]

class Monitor:
    def __init__(
            self, 
            connect: Connect,
            retry_delay: float = 5.0,
            clock: Callable[[], float] = time.monotonic,
    ):
        self._connect = connect
        self._retry_delay = retry_delay
        self._clock = clock
        self._state = MonitorState()
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def latest(self) -> MonitorState:
        with self._lock:
            return self._state

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2)

    def _update(self, **changes) -> None:
        with self._lock:
            self._state = replace(self._state, **changes)

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                with self._connect() as sources:
                    self._update(connected=True, error = None)
                    while not self._stop.is_set():
                        status = read_status_from(sources, timeout=0.5)
                        if status is not None:
                            self._update(status=status, updated_at=self._clock())
            except Exception as exc: # unplugged dongle, read failure, etc
                self._update(connected=False, error=str(exc))
                self._stop.wait(self._retry_delay)