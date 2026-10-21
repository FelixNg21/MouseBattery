import time

from mousebattery.monitor import Monitor
from mousebattery.reader import open_status_channels

monitor = Monitor(open_status_channels, retry_delay=1)
monitor.start()
time.sleep(6)
print(monitor.latest())
monitor.stop()