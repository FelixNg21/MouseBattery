import time
from contextlib import contextmanager

from mousebattery.monitor import Monitor
from mousebattery.reader import DeviceNotFound
from tests.helpers import make_packet


class FakeSource:
    def __init__(self, packets):
        self._packets = list(packets)

    def read(self, length, timeout_ms=0):
        if self._packets:
            return self._packets.pop(0)
        time.sleep(0.01)
        return b""


class ExplodingSource(FakeSource):
    """Delivers its packets, then fails like an unplugged device."""

    def read(self, length, timeout_ms=0):
        if self._packets:
            return self._packets.pop(0)
        raise OSError("device removed")


def scripted_connect(*attempts):
    """Each connect() call consumes one attempt: a list of sources, or an exception."""
    attempts = list(attempts)

    @contextmanager
    def connect():
        attempt = attempts.pop(0) if attempts else DeviceNotFound("gone")
        if isinstance(attempt, Exception):
            raise attempt
        yield attempt

    return connect


def wait_for(condition, timeout=2.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.01)
    return False


def run_monitor(connect):
    monitor = Monitor(connect, retry_delay=0.01)
    monitor.start()
    return monitor


def test_records_status():
    monitor = run_monitor(scripted_connect([FakeSource([make_packet(byte1=0x4A)])]))
    try:
        assert wait_for(lambda: monitor.latest().status is not None)
        state = monitor.latest()
        assert state.status.battery_percent == 74
        assert state.connected
        assert state.updated_at is not None
    finally:
        monitor.stop()


def test_retries_until_dongle_appears():
    monitor = run_monitor(
        scripted_connect(
            DeviceNotFound("unplugged"),
            [FakeSource([make_packet(byte1=0x64)])],
        )
    )
    try:
        assert wait_for(lambda: monitor.latest().status is not None)
        assert monitor.latest().status.battery_percent == 100
    finally:
        monitor.stop()


def test_keeps_last_status_after_disconnect():
    monitor = run_monitor(scripted_connect([ExplodingSource([make_packet(byte1=0x56)])]))
    try:
        assert wait_for(lambda: not monitor.latest().connected and monitor.latest().status)
        state = monitor.latest()
        assert state.status.battery_percent == 86  # still shown, just flagged
        assert state.error is not None
    finally:
        monitor.stop()