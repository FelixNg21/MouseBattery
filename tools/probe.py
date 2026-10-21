from mousebattery import config
from mousebattery.device import HidChannel
from mousebattery.discovery import list_interfaces

for iface in list_interfaces(config.VENDOR_ID, config.TARGET_PRODUCT_IDS):
    if iface.usage_page != config.STATUS_USAGE_PAGE:
        continue
    print(iface.describe())
    try:
        with HidChannel(iface) as channel:
            for _ in range(5):
                data = channel.read(33, timeout_ms=1000)
                print("   ", data.hex(" ") if data else "(timeout)")
    except Exception as exc:
        print("    FAILED:", exc)