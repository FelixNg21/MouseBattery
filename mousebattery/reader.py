from __future__ import annotations

import time
from contextlib import ExitStack
from typing import Protocol

from .device import HidChannel
from .discovery import HidInterface
from .status import parse_status, StatusReport

_READ_LENGTH = 33

class PacketSource(Protocol):
    def read(self, length: int, timeout_ms: int) -> bytes: ...

def read_status_from(
        sources: list[PacketSource], timeout: float = 10.0
) -> StatusReport | None:
    """Poll the sources until a status report arrives or the timeout passes."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for source in sources:
            data = source.read(_READ_LENGTH, timeout_ms=200)
            status = parse_status(data) if data else None
            if status is not None:
                return status
    return None

def read_status(interfaces: list[HidInterface], timeout: float = 10.0) -> StatusReport | None:
    """Open the real HID interfaces and wait for a status report."""
    with ExitStack as stack:
        channels = [stack.enter_context(HidChannel(i)) for i in interfaces]
        return read_status_from(channels, timeout)
  
