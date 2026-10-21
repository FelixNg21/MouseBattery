from mousebattery.discovery import HidInterface
from mousebattery.reader import select_status_interfaces


def iface(vid, pid, number, page, usage=0x1):
    return HidInterface(vid, pid, number, page, usage, "", "test", b"path")


# The dongle's seven interfaces, as enumerated on the real device.
DONGLE = [
    iface(0x093A, 0x522C, 0, 0x01, 0x06),
    iface(0x093A, 0x522C, 1, 0x01, 0x02),
    iface(0x093A, 0x522C, 1, 0x01, 0x80),
    iface(0x093A, 0x522C, 1, 0x0C),
    iface(0x093A, 0x522C, 1, 0xFF00),
    iface(0x093A, 0x522C, 2, 0xFF05),
    iface(0x093A, 0x522C, 2, 0xFF05),
]


def test_keeps_only_the_two_status_interfaces():
    selected = select_status_interfaces(DONGLE)
    assert len(selected) == 2
    assert all(i.usage_page == 0xFF05 and i.interface_number == 2 for i in selected)


def test_ignores_other_devices_with_the_same_usage_page():
    decoy = iface(0x7667, 0x0005, 1, 0xFF05)
    assert select_status_interfaces(DONGLE + [decoy]) == select_status_interfaces(DONGLE)


def test_wired_mode_is_also_matched():
    wired = iface(0x093A, 0x622C, 2, 0xFF05)
    assert wired in select_status_interfaces([wired])


def test_nothing_plugged_in():
    assert select_status_interfaces([]) == []