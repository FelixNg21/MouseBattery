"""Command-line entry point. Each step adds a subcommand."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from . import config
from .battery import read_battery
from .capture import listen
from .discovery import list_interfaces
from .descriptor import parse_descriptor
from .device import HidChannel


def _hex(value: str) -> int:
    return int(value, 16)


def cmd_list(args: argparse.Namespace) -> int:
    if args.all:
        interfaces = list_interfaces()
    else:
        interfaces = list_interfaces(args.vid, tuple(args.pid))

    if not interfaces:
        print("No matching HID interfaces found. Is the dongle plugged in?")
        return 1

    for iface in interfaces:
        print(iface.describe())
    return 0

def cmd_descriptor(args: argparse.Namespace) -> int:
    interfaces = [
        i for i in list_interfaces(args.vid, tuple(args.pid)) if i.is_vendor_defined
    ]

    if not interfaces:
        print("No vendor-defined interfaces found. Is the dongle plugged in?")
        return 1

    for iface in interfaces:
        print(f"=== {iface.describe()}")
        try:
            with HidChannel(iface) as channel:
                desc = channel.report_descriptor()
        except Exception as e:
            print(f"Failed to read descriptor: {e}")
            continue
        print(f" raw : {desc.hex(' ')}")
        print(parse_descriptor(desc).format())
        print()
    return 0

def cmd_listen(args:argparse.Namespace) -> int:
    interfaces = [
        i for i in list_interfaces(args.vid, tuple(args.pid)) if i.usage_page == config.STATUS_USAGE_PAGE
    ]

    if not interfaces:
        print("No 0xff05 interfaces found. Is the dongle plugged in?")
        return 1

    log_path = Path("captures") / f"capture-{datetime.now():%Y%m%d-%H%M%S}.log"
    listen(interfaces, length=33, seconds=args.seconds, log_path=log_path)
    return 0

def cmd_battery(args: argparse.Namespace) -> int:
    interfaces = [
        i for i in list_interfaces(args.vid, tuple(args.pid)) if i.usage_page == config.STATUS_USAGE_PAGE
    ]

    if not interfaces:
        print("No 0xff05 interfaces found. Is the dongle plugged in?")
        return 1

    status = read_battery(interfaces, timeout=args.timeout)
    if status is None:
        print("Failed to read battery status.")
        return 1

    print(f"Battery: {status.percent}% {'(charging)' if status.charging else '(not charging)'}")
    return 0

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mousebattery")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List HID interfaces")
    p_list.add_argument("--all", action="store_true", help="Show every HID device")
    p_list.add_argument("--vid", type=_hex, default=config.VENDOR_ID, help="Vendor ID (hex)")
    p_list.add_argument(
        "--pid", type=_hex, nargs="+", default=list(config.TARGET_PRODUCT_IDS),
        help="Product ID(s) (hex)",
    )
    p_list.set_defaults(func=cmd_list)

    p_descriptor = sub.add_parser("descriptor", help="Read HID report descriptor")
    p_descriptor.add_argument("--vid", type=_hex, default=config.VENDOR_ID, help="Vendor ID (hex)")
    p_descriptor.add_argument(
        "--pid", type=_hex, nargs="+", default=list(config.TARGET_PRODUCT_IDS),
        help="Product ID(s) (hex)",
    )
    p_descriptor.set_defaults(func=cmd_descriptor)

    p_listen = sub.add_parser("listen", help="Passively record incoming reports")
    p_listen.add_argument("--vid", type=_hex, default=config.VENDOR_ID)
    p_listen.add_argument("--pid", type=_hex, nargs="+", default=list(config.TARGET_PRODUCT_IDS))
    p_listen.add_argument("--seconds", type=float, help="Stop after N seconds")
    p_listen.set_defaults(func=cmd_listen)

    p_battery = sub.add_parser("battery", help="Read battery status")
    p_battery.add_argument("--vid", type=_hex, default=config.VENDOR_ID, help="Vendor ID (hex)")
    p_battery.add_argument(
        "--pid", type=_hex, nargs="+", default=list(config.TARGET_PRODUCT_IDS),
        help="Product ID(s) (hex)",
    )
    p_battery.add_argument("--timeout", type=float, default=10.0, help="Timeout in seconds")
    p_battery.set_defaults(func=cmd_battery)

    
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)
