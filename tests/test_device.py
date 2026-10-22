import pytest

from mousebattery.device import HidChannel
from mousebattery.discovery import HidInterface


class FakeDevice:
    def __init__(self, error_text=""):
        self._error_text = error_text

    def read(self, length, timeout_ms):
        raise OSError("read error")

    def error(self):
        return self._error_text


def make_channel(device):
    iface = HidInterface(0x093A, 0x522C, 2, 0xFF05, 0x01, "", "test", b"path")
    channel = HidChannel(iface)
    channel._dev = device
    return channel


def test_read_error_names_the_interface_and_os_detail():
    channel = make_channel(FakeDevice("device not connected"))
    with pytest.raises(OSError) as info:
        channel.read()
    message = str(info.value)
    assert "if2/0xff05" in message
    assert "device not connected" in message


def test_read_error_without_os_detail():
    channel = make_channel(FakeDevice(""))
    with pytest.raises(OSError) as info:
        channel.read()
    assert str(info.value) == "read error on if2/0xff05"