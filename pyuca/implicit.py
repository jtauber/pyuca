"""Implicit collation weights for code points absent from the DUCET table.

Follows the Unicode Collation Algorithm (UTS #10, section 10.1). Most code
points get their weights from ``allkeys.txt``; CJK ideographs and a few large
scripts (Tangut, Nushu, Khitan Small Script, ...) are weighted implicitly.

The script-block bases are declared per Unicode version by ``@implicitweights``
directives in the data file, so they need no code here -- they are passed in as
``implicit_ranges``. The Han ranges below follow *fixed* Unicode block
allocations rather than the last assigned code point, so newly assigned
ideographs within a block are handled without any per-version tables.
"""

import unicodedata
from typing import TypeAlias

CollationElement: TypeAlias = list[int]
CollationElements: TypeAlias = list[CollationElement]
# (start, end, base, origin) derived from an @implicitweights directive.
# ``origin`` is the start of the first directive sharing this ``base``: several
# ranges may share a base (e.g. Tangut and Tangut Supplement both use 0xFB00),
# and the second collation weight is an offset measured from that shared origin.
ImplicitRange: TypeAlias = tuple[int, int, int, int]

# CJK Unified Ideographs block -> base 0xFB40 ("core" Han).
_CORE_HAN_START = 0x4E00
_CORE_HAN_END = 0x9FFF

# The twelve CJK Compatibility Ideographs with no canonical decomposition.
# Unlike the rest of that block they survive NFD normalization and are then
# weighted as core Han.
_CORE_HAN_COMPAT = frozenset(
    {
        0xFA0E,
        0xFA0F,
        0xFA11,
        0xFA13,
        0xFA14,
        0xFA1F,
        0xFA21,
        0xFA23,
        0xFA24,
        0xFA27,
        0xFA28,
        0xFA29,
    }
)

# CJK Unified Ideographs Extension blocks -> base 0xFB80 ("extension" Han).
# These are the full block allocations (see Unicode Blocks.txt), so assignments
# added within a block in a later Unicode version fall through automatically.
_EXTENSION_HAN_RANGES: tuple[tuple[int, int], ...] = (
    (0x3400, 0x4DBF),  # Extension A
    (0x20000, 0x2A6DF),  # Extension B
    (0x2A700, 0x2B73F),  # Extension C
    (0x2B740, 0x2B81F),  # Extension D
    (0x2B820, 0x2CEAF),  # Extension E
    (0x2CEB0, 0x2EBEF),  # Extension F
    (0x2EBF0, 0x2EE5F),  # Extension I  (Unicode 15.1)
    (0x30000, 0x3134F),  # Extension G  (Unicode 13.0)
    (0x31350, 0x323AF),  # Extension H  (Unicode 15.0)
)

_CORE_HAN_BASE = 0xFB40
_EXTENSION_HAN_BASE = 0xFB80
_UNASSIGNED_BASE = 0xFBC0


def _is_core_han(cp: int) -> bool:
    return _CORE_HAN_START <= cp <= _CORE_HAN_END or cp in _CORE_HAN_COMPAT


def _is_extension_han(cp: int) -> bool:
    return any(start <= cp <= end for start, end in _EXTENSION_HAN_RANGES)


def implicit_weight(cp: int, implicit_ranges: list[ImplicitRange]) -> CollationElements:
    """Return the implicit collation elements for code point ``cp``.

    ``implicit_ranges`` are the ``@implicitweights`` directives parsed from the
    active DUCET file, in file order.
    """
    assigned = unicodedata.category(chr(cp)) != "Cn"

    if assigned and _is_core_han(cp):
        base, origin = _CORE_HAN_BASE, 0
    elif assigned and _is_extension_han(cp):
        base, origin = _EXTENSION_HAN_BASE, 0
    else:
        base, origin = _UNASSIGNED_BASE, 0
        for start, end, range_base, range_origin in implicit_ranges:
            if start <= cp <= end:
                base, origin = range_base, range_origin
                break

    offset = cp - origin
    aaaa = base + (offset >> 15)
    bbbb = (offset & 0x7FFF) | 0x8000
    return [[aaaa, 0x0020, 0x0002], [bbbb, 0x0000, 0x0000]]
