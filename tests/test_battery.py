from mousebattery.battery import BatteryStatus, parse_status_report

def test_charging():
    assert parse_status_report(bytes.fromhex("09 ca 20 08")) == BatteryStatus(74, True)

def test_not_charging():
    assert parse_status_report(bytes.fromhex("09 4a 20 08")) == BatteryStatus(74, False)

def test_other_report_ids_ignored():
    assert parse_status_report(bytes.fromhex("08 4a 20 08")) is None

def test_too_short():
    assert parse_status_report(b"\x09") is None