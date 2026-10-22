from __future__ import annotations
import hid
from .discovery import HidInterface

class HidChannel:
    def __init__(self, interface: HidInterface):
        self.interface = interface
        self._dev: hid.device | None = None

    def open(self) -> "HidChannel":
        dev = hid.device()
        dev.open_path(self.interface.path)
        self._dev = dev
        return self

    def close(self) -> None:
        if self._dev is not None:
            self._dev.close()
            self._dev = None

    def __enter__(self) -> "HidChannel":
        return self.open()

    def __exit__(self, *exc) -> None:
        self.close()

    def report_descriptor(self) -> bytes:
        return bytes(self._dev.get_report_descriptor())

    def read(self, length: int = 64, timeout_ms: int = 500) -> bytes:
        """Blocking read. Returns b'' if nothing arrives before the timeout."""
        try:
            return bytes(self._dev.read(length, timeout_ms))
        except OSError as exc:
            iface = self.interface
            where = f"if{iface.interface_number}/{iface.usage_page:#06x}"
            detail = self._dev.error()
            raise OSError(f"{exc} on {where}" + (f": {detail}" if detail else "")) from exc