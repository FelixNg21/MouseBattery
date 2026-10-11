from __future__ import annotations

import threading
import time
from datetime import datetime
from pathlib import Path

from .device import HidChannel
from .discovery import HidInterface

def listen(
        interfaces: list[HidInterface],
        length: int,
        seconds: float | None,
        log_path: Path
) -> None:
    stop = threading.Event()
    lock = threading.Lock()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_file = open(log_path, "a", encoding="utf-8")

    def emit(label: str, text: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        line = f"{stamp} {label} {text}\n"
        with lock:
            print(line, end="")
            log_file.write(line)
            log_file.flush()

    def reader(iface: HidInterface, label: str) -> None:
        try:
            with HidChannel(iface) as channel:
                emit(label, "listening")
                while not stop.is_set():
                    data = channel.read(length, timeout_ms=500)
                    if data:
                        emit(label, data.hex(" "))
        except Exception as exc:
            emit(label, f"error: {exc}")

    threads = []
    for n, iface in enumerate(interfaces):
        label = f"ch{n} if{iface.interface_number} / {iface.usage_page:#06x}"
        thread = threading.Thread(target=reader, args=(iface, label), daemon=True)
        thread.start()
        threads.append(thread)

    try:
        if seconds:
            time.sleep(seconds)
        else:
            print("Type a note and press Enter to mark an event. Ctrl+C to stop.")
            while True:
                text = input().strip()
                if text:
                    emit("NOTE", text)
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        stop.set()
        for thread in threads:
            thread.join()
        log_file.close()