"""Bundle the built exe into a release zip, plus a SHA-256 checksum file.

Run from the project root, AFTER building with `python build_exe.py --onefile`:

    python -m scripts.package_release

(`-m` matters: running the file directly would put scripts/ on the import path
instead of the project root, and `import mousebattery` would fail.)
"""

from __future__ import annotations

import sys
from pathlib import Path
import hashlib
import zipfile

EXE = Path("dist") / "MouseBattery.exe"
EXTRA_FILES = [Path("README.md"), Path("LICENSE"), Path("THIRD_PARTY_NOTICES.md")]
OUT_DIR = Path("release")
CHUNK_SIZE = 64 * 1024


def release_basename(version: str) -> str:
    """Name used for the zip and the folder inside it, e.g. "MouseBattery-0.1.0-windows".
    """
    return f"MouseBattery-{version}-windows"


def sha256_of(path: Path) -> str:
    """Hex SHA-256 digest of a file.

    TODO: look up hashlib.sha256 and its .update() method. Read the file in chunks
    (for example 64 KiB at a time) so a large file never has to fit in memory.
    """
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def checksum_line(path: Path) -> str:
    """One line in the format the `sha256sum` tool writes: "<hash>  <filename>".

    Two spaces between them, and the filename only (no directory part).
    """
    return f"{sha256_of(path)}  {path.name}"


def build_zip(files: list[Path], out_path: Path, folder: str) -> None:
    """Zip `files` into `out_path`, all inside one top-level `folder` in the archive.

    So unzipping gives a single tidy folder instead of loose files.
    Look up zipfile.ZipFile and its `arcname` argument.
    If any file is missing, raise FileNotFoundError BEFORE creating the zip, so a
    half-made archive is never left behind.
    """
    for file in files:
        if not file.is_file():
            raise FileNotFoundError(file)
    z = zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED)
    for file in files:
        z.write(file, f"{folder}/{file.name}")
    z.close()



def main() -> int:
    from mousebattery import __version__  # TODO (README): where does this come from?

    if not EXE.is_file():
        print(f"error: {EXE} not found. Build it first: python build_exe.py --onefile", file=sys.stderr)
        return 1
    missing = [str(p) for p in EXTRA_FILES if not p.is_file()]
    if missing:
        print(f"error: missing file(s): {', '.join(missing)}", file=sys.stderr)
        return 1

    folder = release_basename(__version__)
    OUT_DIR.mkdir(exist_ok=True)
    zip_path = OUT_DIR / f"{folder}.zip"
    build_zip([EXE, *EXTRA_FILES], zip_path, folder)

    checksum_path = zip_path.with_name(zip_path.name + ".sha256")
    checksum_path.write_text(checksum_line(zip_path) + "\n", encoding="utf-8")

    print(f"Wrote {zip_path}")
    print(f"Wrote {checksum_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
