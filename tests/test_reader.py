from mousebattery.reader import read_status_from
from tests.helpers import make_packet

class FakeSource:
    """Hands out queued packets, then returns b'' (like a read timeout)"""

    def __init__(self, packets):
        self._packets = list(packets)

    def read(self, length, timeout_ms=0):
        return self._packets.pop(0) if self._packets else b''

def test_returns_first_valid_status():
    source = FakeSource([make_packet(byte1=0x4A)])
    status = read_status_from([source], timeout= 1)
    assert status.battery_percent == 74

def test_skips_non_status_reports():
    other = bytearray(make_packet())
    other[0] = 0x08 
    source = FakeSource([bytes(other), make_packet(byte1=0x56)])
    status = read_status_from([source], timeout=1)
    assert status.battery_percent == 86

def test_times_out_with_none():
    assert read_status_from([FakeSource([])], timeout=0.05) is None

def test_uses_whichever_source_has_data():
    silent = FakeSource([])
    talking = FakeSource([make_packet(byte1=0x64)])
    status = read_status_from([silent, talking], timeout=1)
    assert status.battery_percent == 100