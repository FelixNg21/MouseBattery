import traceback

from mousebattery.reader import open_status_channels, read_status_from

try:
    with open_status_channels() as sources:
        print("opened", len(sources), "channels")
        print(read_status_from(sources, timeout=15))
except Exception:
    traceback.print_exc()