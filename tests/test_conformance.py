"""Official UCA conformance suite (variable weighting: Non-ignorable).

A collator's conformance can only be checked on an interpreter whose
``unicodedata`` matches that UCA version, because ``sort_key`` uses the runtime
for NFD normalization and combining classes. Each version is therefore only
exercised on its matching runtime; on any given Python the rest are skipped.
"""

import gzip
import unicodedata
from pathlib import Path

import pytest

from pyuca.collator import available_versions, select_collator

CONFORMANCE_DIR = Path(__file__).resolve().parent.parent / "CollationTest"
RUNTIME_UNICODE = unicodedata.unidata_version


def _test_strings(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            points = line.split("#", 1)[0].split(";", 1)[0].strip().split()
            if points:
                yield "".join(chr(int(p, 16)) for p in points)


@pytest.mark.parametrize("version", available_versions())
def test_non_ignorable_conformance(version):
    if version != RUNTIME_UNICODE:
        pytest.skip(
            f"runtime Unicode {RUNTIME_UNICODE} != {version}; "
            "NFD data would not match the DUCET"
        )
    path = CONFORMANCE_DIR / version / "CollationTest_NON_IGNORABLE.txt.gz"
    if not path.exists():
        pytest.skip(f"no conformance fixture bundled for {version}")

    collator = select_collator(version)()
    previous = None
    for lineno, string in enumerate(_test_strings(path), 1):
        key = collator.sort_key(string)
        if previous is not None:
            assert previous <= key, f"non-monotonic at fixture line {lineno}"
        previous = key


def test_runtime_version_is_covered():
    # Guard against the whole suite silently skipping: the running interpreter
    # must have a matching bundled conformance fixture (true for 3.11-3.14).
    assert RUNTIME_UNICODE in available_versions()
