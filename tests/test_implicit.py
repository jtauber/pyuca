"""Deterministic unit tests for implicit weighting (independent of runtime)."""

from pyuca.implicit import implicit_weight


def test_core_han_uro():
    # U+4E00 is a core Han ideograph -> base 0xFB40.
    assert implicit_weight(0x4E00, []) == [[0xFB40, 0x0020, 0x0002], [0xCE00, 0, 0]]


def test_core_han_noncomposing_compatibility_ideograph():
    # U+FA0E has no canonical decomposition and is weighted as core Han.
    # It is above U+8000, so AAAA = 0xFB40 + (cp >> 15) = 0xFB41.
    assert implicit_weight(0xFA0E, []) == [[0xFB41, 0x0020, 0x0002], [0xFA0E, 0, 0]]


def test_extension_han():
    # U+3400 (Extension A) -> base 0xFB80.
    assert implicit_weight(0x3400, [])[0][0] == 0xFB80


def test_implicit_range_uses_shared_origin():
    # Tangut and Tangut Supplement share base 0xFB00; the supplement's offset
    # is measured from the Tangut origin (0x17000), not its own start.
    ranges = [
        (0x17000, 0x18AFF, 0xFB00, 0x17000),
        (0x18D00, 0x18D8F, 0xFB00, 0x17000),
    ]
    assert implicit_weight(0x18D00, ranges) == [
        [0xFB00, 0x0020, 0x0002],
        [0x9D00, 0, 0],
    ]


def test_first_range_start_is_its_own_origin():
    ranges = [(0x17000, 0x18AFF, 0xFB00, 0x17000)]
    assert implicit_weight(0x17000, ranges) == [
        [0xFB00, 0x0020, 0x0002],
        [0x8000, 0, 0],
    ]


def test_unassigned_falls_back_to_fbc0():
    # U+FFFF is a noncharacter (unassigned) -> base 0xFBC0 + (cp >> 15).
    ce = implicit_weight(0xFFFF, [])
    assert ce[0][0] == 0xFBC0 + (0xFFFF >> 15)
    assert ce[1][0] == (0xFFFF & 0x7FFF) | 0x8000
