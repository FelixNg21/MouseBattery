from __future__ import annotations
from dataclasses import dataclass

STATUS_REPORT_ID = 0x09

# Temporary
POLLING_RATES_HZ = {0: 1000, 1: 500, 2: 250, 3: 125}

@dataclass(frozen=True)
class StatusReport:
    battery_percent: int
    charging: bool
    dpi_stage: int
    dpi: int
    polling_hz: int | None

def dpi_from_register(value: int) -> int:
    """Convert a DPI register value to a DPI value."""
    return (value+1) * 50

def parse_status(data: bytes) -> StatusReport | None:
    """Decode a status report, or return None."""
    if len(data) < 7 or data[0] != STATUS_REPORT_ID:
        return None
    percent = data[1] & 0x7F
    if percent > 100:
        return None
    return StatusReport(
        battery_percent=percent,
        charging=bool(data[1] & 0x80),
        dpi_stage=data[2] >> 4,
        dpi=dpi_from_register(data[5]),
        polling_hz=POLLING_RATES_HZ.get(data[2] & 0x0F),
    )