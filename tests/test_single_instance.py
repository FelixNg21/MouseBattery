import uuid

import pytest

from mousebattery.single_instance import SingleInstance  # noqa: E402


def unique_name():
    return f"mousebattery-test-{uuid.uuid4().hex}"


def test_first_instance_gets_the_lock():
    guard = SingleInstance(unique_name())
    try:
        assert guard.acquire()
    finally:
        guard.release()


def test_second_instance_is_refused():
    name = unique_name()
    first, second = SingleInstance(name), SingleInstance(name)
    try:
        assert first.acquire()
        assert not second.acquire()
    finally:
        first.release()
        second.release()


def test_lock_can_be_taken_again_after_release():
    name = unique_name()
    first, second = SingleInstance(name), SingleInstance(name)
    try:
        assert first.acquire()
        first.release()
        assert second.acquire()
    finally:
        second.release()


def test_release_twice_is_harmless():
    guard = SingleInstance(unique_name())
    guard.acquire()
    guard.release()
    guard.release()


def test_different_names_do_not_conflict():
    a, b = SingleInstance(unique_name()), SingleInstance(unique_name())
    try:
        assert a.acquire()
        assert b.acquire()
    finally:
        a.release()
        b.release()
