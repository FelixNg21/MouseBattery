import logging
import sys
import threading
from types import SimpleNamespace

import pytest

from mousebattery.logging_setup import log_path, setup_logging


@pytest.fixture(autouse=True)
def clean_logging():
    saved = (sys.excepthook, threading.excepthook)
    yield
    logger = logging.getLogger("mousebattery")
    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)
    logger.setLevel(logging.NOTSET)
    sys.excepthook, threading.excepthook = saved


def test_log_path_uses_localappdata(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert log_path() == tmp_path / "mousebattery" / "mousebattery.log"


def test_messages_reach_the_file(tmp_path):
    path = tmp_path / "logs" / "app.log"
    setup_logging(path)
    logging.getLogger("mousebattery.test").info("hello log")
    assert "hello log" in path.read_text(encoding="utf-8")


def test_calling_twice_does_not_duplicate_lines(tmp_path):
    path = tmp_path / "app.log"
    setup_logging(path)
    setup_logging(path)
    logging.getLogger("mousebattery.test").info("only once")
    assert path.read_text(encoding="utf-8").count("only once") == 1


def test_uncaught_exception_is_logged_with_traceback(tmp_path):
    path = tmp_path / "app.log"
    setup_logging(path)
    try:
        raise ValueError("boom")
    except ValueError:
        sys.excepthook(*sys.exc_info())
    text = path.read_text(encoding="utf-8")
    assert "boom" in text and "Traceback" in text


def test_uncaught_thread_exception_is_logged(tmp_path):
    path = tmp_path / "app.log"
    setup_logging(path)
    try:
        raise ValueError("thread boom")
    except ValueError as exc:
        args = SimpleNamespace(
            exc_type=type(exc),
            exc_value=exc,
            exc_traceback=exc.__traceback__,
            thread=threading.current_thread(),
        )
    threading.excepthook(args)
    assert "thread boom" in path.read_text(encoding="utf-8")