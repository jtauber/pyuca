import unicodedata

from pyuca import Collator, __version__
from pyuca.collator import select_collator


def test_cafe_ordering():
    c = Collator()
    # Plain sort ignores the accent's real collation position.
    assert sorted(["cafe", "caff", "café"]) == ["cafe", "caff", "café"]
    # UCA: accents only break ties at the primary level, so café < caff.
    assert sorted(["cafe", "caff", "café"], key=c.sort_key) == [
        "cafe",
        "café",
        "caff",
    ]


def test_default_matches_runtime_unicode():
    # The whole point of the redesign: the default collator tracks the
    # interpreter's Unicode version rather than sys.version_info.
    assert Collator is select_collator(unicodedata.unidata_version)


def test_version_string_available():
    assert isinstance(__version__, str) and __version__
