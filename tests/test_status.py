import pytest

from mousebattery.status import dpi_from_register, parse_status
from tests.helpers import make_packet

def test_full_packet():
    status = parse_status(make_packet(byte2=0x23))
    assert status.battery_percent == 86
    assert not status.charging
    assert status.dpi_stage == 2
    assert status.dpi == 1500
    assert status.polling_hz == 125

def test_charging():
    status = parse_status(make_packet(byte1=0xE2))
    assert status.charging
    assert status.battery_percent == 98

def test_not_charging():
    status = parse_status(make_packet(byte1=0x4A))
    assert not status.charging
    assert status.battery_percent == 74

def test_full_battery_without_flag():
    assert parse_status(make_packet(byte1=0x64)).battery_percent == 100

def test_wrong_report_id():
    packet = bytearray(make_packet())
    packet[0] = 0x08
    assert parse_status(bytes(packet)) is None

def test_too_short():
    assert parse_status(b"\x09") is None

def test_percent_out_of_range():
    assert parse_status(make_packet(byte1=0x7F)) is None
    
@pytest.mark.parametrize("register, dpi",
                         [(0x07, 400), (0x0F, 800), (0x1D, 1500), (0x2F, 2400), (0x3F, 3200), (0x7F, 6400)],)
def test_dpi_from_register(register, dpi):
    assert dpi_from_register(register) == dpi