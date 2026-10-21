from mousebattery.display import describe, level_color
from mousebattery.monitor import MonitorState
from mousebattery.status import StatusReport

def report(percent=87, charging=False):
    return StatusReport(percent, charging, 2, 1500, 1000)

def test_no_dongle():
    assert describe(MonitorState(), now=0) == "Incott G23: dongle not found"

def test_waiting_for_mouse():
    assert describe(MonitorState(connected=True), now=0) == "Incott G23: waiting for mouse..."

def test_fresh_reading():
    state = MonitorState(report(), updated_at=100, connected=True)
    assert describe(state, now=110) == "Incott G23: 87%"


def test_charging():
    state = MonitorState(report(charging=True), updated_at=100, connected=True)
    assert describe(state, now=110) == "Incott G23: 87% (charging)"


def test_stale_reading():
    state = MonitorState(report(), updated_at=0, connected=True)
    assert describe(state, now=300) == "Incott G23: 87%, updated 5 min ago"


def test_disconnected_after_reading():
    state = MonitorState(report(), updated_at=100, connected=False)
    assert describe(state, now=110) == "Incott G23: 87%, dongle disconnected"


def test_colors_by_level():
    assert level_color(None) != level_color(50)
    assert level_color(50) != level_color(25) != level_color(10)