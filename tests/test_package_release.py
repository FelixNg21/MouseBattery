import hashlib
import zipfile

import pytest

from scripts.package_release import (  # noqa: E402
    build_zip,
    checksum_line,
    release_basename,
    sha256_of,
)

ABC_SHA256 = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_release_basename():
    assert release_basename("0.1.0") == "MouseBattery-0.1.0-windows"


def test_sha256_of_known_content(tmp_path):
    f = tmp_path / "a.bin"
    f.write_bytes(b"abc")
    assert sha256_of(f) == ABC_SHA256


def test_sha256_of_a_file_larger_than_one_chunk(tmp_path):
    data = b"x" * (5 * 1024 * 1024)
    f = tmp_path / "big.bin"
    f.write_bytes(data)
    assert sha256_of(f) == hashlib.sha256(data).hexdigest()


def test_checksum_line_format(tmp_path):
    f = tmp_path / "MouseBattery.zip"
    f.write_bytes(b"abc")
    assert checksum_line(f) == f"{ABC_SHA256}  MouseBattery.zip"


def test_zip_puts_files_in_one_top_level_folder(tmp_path):
    a, b = tmp_path / "a.txt", tmp_path / "b.txt"
    a.write_text("first")
    b.write_text("second")
    out = tmp_path / "out.zip"
    build_zip([a, b], out, "MouseBattery-0.1.0-windows")
    with zipfile.ZipFile(out) as z:
        assert sorted(z.namelist()) == [
            "MouseBattery-0.1.0-windows/a.txt",
            "MouseBattery-0.1.0-windows/b.txt",
        ]


def test_zip_keeps_file_contents(tmp_path):
    a = tmp_path / "a.txt"
    a.write_text("hello")
    out = tmp_path / "out.zip"
    build_zip([a], out, "pkg")
    with zipfile.ZipFile(out) as z:
        assert z.read("pkg/a.txt") == b"hello"


def test_missing_file_raises_and_leaves_no_zip(tmp_path):
    out = tmp_path / "out.zip"
    with pytest.raises(FileNotFoundError):
        build_zip([tmp_path / "nope.txt"], out, "pkg")
    assert not out.exists()
