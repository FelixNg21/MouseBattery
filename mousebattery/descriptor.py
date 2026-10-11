from __future__ import annotations
from dataclasses import dataclass

_MAIN_TAGS = {0x8: "input", 0x9: "output", 0xb: "feature"}

_TAG_REPORT_SIZE =  0x7
_TAG_REPORT_ID = 0x8
_TAG_REPORT_COUNT = 0x9

_TYPE_MAIN = 0
_TYPE_GLOBAL = 1

@dataclass
class ReportSpec:
    kind: str
    report_id: int
    bits: int = 0

    @property
    def payload_bytes(self) -> int:
        return (self.bits + 7) // 8

@dataclass
class DescriptorSummary:
    reports: list[ReportSpec]

    def format(self) -> str:
        if not self.reports:
            return " (no reports declared)"

        lines = []
        for r in self.reports:
            rid = f"id={r.report_id:#04x}" if r.report_id else "no report id"
            lines.append(f"  {r.kind:<8} {rid:<14} {r.payload_bytes} bytes payload")
        return "\n".join(lines)

def parse_descriptor(data: bytes) -> DescriptorSummary:
    report_size = report_count = report_id = 0
    specs: dict[tuple[str, int], ReportSpec] = {}

    i = 0
    while i < len(data):
        prefix = data[i]

        if prefix == 0xFE:
            length = data[i + 1] if i + 1 < len(data) else 0
            i += 3 + length
            continue

        size = prefix & 0x03
        size = 4 if size == 3 else size
        item_type = (prefix >> 2) & 0x03
        tag = prefix >> 4
        value = int.from_bytes(data[i + 1:i + 1 + size], "little")
        i += 1 + size

        if item_type == _TYPE_GLOBAL:
            if tag == _TAG_REPORT_SIZE:
                report_size = value
            elif tag == _TAG_REPORT_COUNT:
                report_count = value
            elif tag == _TAG_REPORT_ID:
                report_id = value
        elif item_type == _TYPE_MAIN and tag in _MAIN_TAGS:
            kind = _MAIN_TAGS[tag]
            spec = specs.setdefault((kind, report_id), ReportSpec(kind, report_id))
            spec.bits += report_size * report_count

    return DescriptorSummary(list(specs.values()))