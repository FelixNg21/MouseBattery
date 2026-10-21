from __future__ import annotations

import time
from contextlib import ExitStack, contextmanager
from typing import Protocol, Iterator

from . import config
from .device import HidChannel
from .discovery import HidInterface, list_interfaces
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
    with ExitStack() as stack:
        channels = [stack.enter_context(HidChannel(i)) for i in interfaces]
        return read_status_from(channels, timeout)
  
class DeviceNotFound(Exception):
    """The dongle isn't plugged in, or exposes no status interface."""

def select_status_interfaces(interfaces:list[HidInterface]) -> list[HidInterface]:
    """Keep only the interfaces that carry the periodic status report."""
    return [
        i for i in interfaces
        if i.vendor_id == config.VENDOR_ID
        and i.product_id in config.TARGET_PRODUCT_IDS
        and i.usage_page == config.STATUS_USAGE_PAGE
    ]
@contextmanager
def open_status_channels() -> Iterator[list[HidChannel]]:
    interfaces = select_status_interfaces(list_interfaces())
    if not interfaces:
        raise DeviceNotFound("no status interface found")
    with ExitStack() as stack:
        yield [stack.enter_context(HidChannel(i)) for i in interfaces]