from __future__ import annotations

import logging
import os
import sys
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path

APP_NAME = "mousebattery"
_FORMAT = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"
_HANDLER_TAG = "_mousebattery_handler"

def log_path() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    root = Path(base) if base else Path.home() / ".local" / "state"
    return root / APP_NAME / f"{APP_NAME}.log"

def setup_logging(path: Path | None = None) -> Path:
    """Log to a rotating file (and to terminal, if present)."""
    path = path or log_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.INFO)
    for old in [h for h in logger.handlers if getattr(h, _HANDLER_TAG, False)]:
        logger.removeHandler(old)
        old.close()

    handlers: list[logging.Handler] = [
        RotatingFileHandler(path, maxBytes=256 * 1024, backupCount=2, encoding="utf-8")
    ]
    if sys.stderr is not None and sys.stderr.isatty():
        handlers.append(logging.StreamHandler())

    formatter = logging.Formatter(_FORMAT)
    for handler in handlers:
        handler.setFormatter(formatter)
        setattr(handler, _HANDLER_TAG, True)
        logger.addHandler(handler)

    _install_exception_hooks(logger)
    return path

def _install_exception_hooks(logger: logging.Logger) -> None:
    def log_uncaught(exc_type, exc_value, exc_tb) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        logger.critical("uncaught exception", exc_info=(exc_type, exc_value, exc_tb))

    def log_thread_uncaught(args) -> None:
        if args.exc_type is SystemExit:
            return
        name = args.thread.name if args.thread else "?"
        logger.critical(
            "uncaught exception in thread %s",
            name,
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback)
        )

    sys.excepthook = log_uncaught
    threading.excepthook = log_thread_uncaught