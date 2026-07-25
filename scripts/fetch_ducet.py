#!/usr/bin/env python3
"""Fetch and stage Unicode DUCET + conformance data for pyuca.

For each requested UCA version this downloads, from the official Unicode
Consortium site, the DUCET table (``allkeys.txt``) and the collation
conformance suite (``CollationTest.zip``), then writes them into the repo in
the gzipped form pyuca ships and tests against:

    pyuca/allkeys-<version>.txt.gz
    CollationTest/<version>/CollationTest_NON_IGNORABLE.txt.gz
    CollationTest/<version>/CollationTest_SHIFTED.txt.gz

The Unicode site has used two directory layouts over time; both are tried:

    https://www.unicode.org/Public/UCA/<version>/...   (<= 16.0.0)
    https://www.unicode.org/Public/<version>/uca/...    (17.0.0+)

Usage:
    python scripts/fetch_ducet.py                 # the six modern versions
    python scripts/fetch_ducet.py 16.0.0 17.0.0   # specific versions
"""

from __future__ import annotations

import gzip
import io
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PYUCA_DIR = REPO_ROOT / "pyuca"
COLLATION_TEST_DIR = REPO_ROOT / "CollationTest"

# Versions bundled/tested by default (each modern CPython's Unicode + latest).
DEFAULT_VERSIONS = ["13.0.0", "14.0.0", "15.0.0", "15.1.0", "16.0.0", "17.0.0"]

# Conformance suites we extract from CollationTest.zip. NON_IGNORABLE is the
# one pyuca is validated against today; SHIFTED is staged for future work.
CONFORMANCE_FILES = [
    "CollationTest_NON_IGNORABLE.txt",
    "CollationTest_SHIFTED.txt",
]

URL_LAYOUTS = (
    "https://www.unicode.org/Public/UCA/{version}/{name}",
    "https://www.unicode.org/Public/{version}/uca/{name}",
)


def download(version: str, name: str) -> bytes:
    """Return the bytes of ``name`` for ``version``, trying both layouts."""
    last_error: Exception | None = None
    for layout in URL_LAYOUTS:
        url = layout.format(version=version, name=name)
        try:
            with urllib.request.urlopen(url) as response:  # noqa: S310 (trusted host)
                if response.status == 200:
                    print(f"  fetched {url}")
                    return response.read()
        except urllib.error.HTTPError as error:  # pragma: no cover - network
            last_error = error
    raise RuntimeError(f"could not download {name} for {version}: {last_error}")


def write_gzip(data: bytes, destination: Path) -> None:
    """Write ``data`` gzipped to ``destination`` deterministically (mtime=0)."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with gzip.GzipFile(destination, "wb", mtime=0) as gz:
        gz.write(data)
    rel = destination.relative_to(REPO_ROOT)
    print(f"  wrote {rel} ({destination.stat().st_size} bytes)")


def fetch_version(version: str) -> None:
    print(f"UCA {version}:")

    allkeys = download(version, "allkeys.txt")
    write_gzip(allkeys, PYUCA_DIR / f"allkeys-{version}.txt.gz")

    zip_bytes = download(version, "CollationTest.zip")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        members = {Path(n).name: n for n in archive.namelist()}
        for wanted in CONFORMANCE_FILES:
            member = members.get(wanted)
            if member is None:
                print(f"  WARNING: {wanted} not in archive for {version}")
                continue
            content = archive.read(member)
            write_gzip(content, COLLATION_TEST_DIR / version / f"{wanted}.gz")


def main(argv: list[str]) -> int:
    versions = argv or DEFAULT_VERSIONS
    for version in versions:
        fetch_version(version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
