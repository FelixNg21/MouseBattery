from __future__ import annotations

from .monitor import MonitorState

DEVICE_NAME = "Incott G23"
STATLE_AFTER_SECONDS = 120

GREEN = (46, 160, 67)
ORANGE = (230, 126, 34)
RED = (200, 50, 50)
GRAY = (110, 110, 110)

def level_color(percent: int | None) -> tuple[int, int, int]:
    if percent is None:
        return GRAY
    if percent <= 15:
        return RED
    if percent <= 30:
        return ORANGE
    return GREEN

def _ago(seconds: float) -> str:
    minutes = int(seconds // 60)
    if minutes < 60:
        return f"{minutes} min ago"
    return f"{minutes // 60} h ago"

def describe(state: MonitorState, now: float) -> str:
    if state.status is None:
        if state.connected:
            return f"{DEVICE_NAME}: waiting for mouse..."
        return f"{DEVICE_NAME}: dongle not found"

    text = f"{DEVICE_NAME}: {state.status.battery_percent}%"
    if state.status.charging:
        text += " (charging)"
    notes = []
    if state.updated_at is not None and now - state.updated_at > STATLE_AFTER_SECONDS:
        notes.append(f"updated {_ago(now - state.updated_at)}")
    if not state.connected:
        notes.append("dongle disconnected")
    if notes:
        text += ", " + ", ".join(notes)
    return text