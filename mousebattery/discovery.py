"""Step 1: find and describe HID interfaces. No I/O beyond enumeration."""

from __future__ import annotations

from dataclasses import dataclass

import hid

VENDOR_DEFINED_MIN = 0xFF00


@dataclass(frozen=True)
class HidInterface:
    vendor_id: int
    product_id: int
    interface_number: int
    usage_page: int
    usage: int
    manufacturer: str
    product: str
    path: bytes

    @property
    def is_vendor_defined(self) -> bool:
        return self.usage_page >= VENDOR_DEFINED_MIN

    def describe(self) -> str:
        tag = "vendor" if self.is_vendor_defined else "standard"
        return (
            f"{self.vendor_id:04x}:{self.product_id:04x} "
            f"if={self.interface_number:<2} "
            f"page={self.usage_page:#06x} usage={self.usage:#06x} "
            f"[{tag}] {self.product}"
        )


def list_interfaces(
    vendor_id: int | None = None,
    product_ids: tuple[int, ...] | None = None,
) -> list[HidInterface]:
    """Enumerate HID interfaces, optionally filtered by VID and PIDs."""
    found = []
    for d in hid.enumerate(vendor_id or 0, 0):
        if product_ids and d["product_id"] not in product_ids:
            continue
        found.append(
            HidInterface(
                vendor_id=d["vendor_id"],
                product_id=d["product_id"],
                interface_number=d["interface_number"],
                usage_page=d["usage_page"],
                usage=d["usage"],
                manufacturer=d.get("manufacturer_string") or "",
                product=d.get("product_string") or "",
                path=d["path"],
            )
        )
    found.sort(key=lambda i: (i.vendor_id, i.product_id, i.interface_number, i.usage_page))
    return found
