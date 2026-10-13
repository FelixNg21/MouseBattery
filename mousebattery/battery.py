from __future__ import annotations

import time
from contextlib import ExitStack
from dataclasses import dataclass

from .device import HidChannel
from .discovery import HidInterface

STATUS_REPORT_ID = 0x09
_CHARGING_BIT = 0x80
_PERCENT_MASK = 0x7F
_READ_LENGTH = 33

@dataclass(frozen=True)
class BatteryStatus:
    percent: int
    charging: bool

def parse_status_report(data: bytes) -> BatteryStatus | None:
    """Decode a status report, or return None if it isn't one."""
    if len(data) < 2 or data[0] != STATUS_REPORT_ID:
        return None
    percent = data[1] & _PERCENT_MASK
    if percent > 100:
        return None
    return BatteryStatus(percent=percent, charging=bool(data[1] & _CHARGING_BIT))

def read_battery(interfaces: list[HidInterface], timeout: float = 10.0) -> BatteryStatus | None:
    """Wait for the next status report. Returns None if none arrives in time."""
    deadline = time.monotonic() + timeout
    with ExitStack() as stack:
        channels = [stack.enter_context(HidChannel(i)) for i in interfaces]
        while time.monotonic() < deadline:
            for channel in channels:
                data = channel.read(_READ_LENGTH, timeout_ms=200)
                if data:
                    status = parse_status_report(data) if data else None
                    if status is not None:
                        return status
    return None