"""Python implementation of the Unicode Collation Algorithm (UTS #10).

The default :data:`Collator` is chosen to match the Unicode version of the
running interpreter's :mod:`unicodedata` (``unicodedata.unidata_version``),
because ``sort_key`` relies on that module for NFD normalization and combining
classes. Version-specific collators (``Collator_16_0_0`` etc.) can also be
imported directly.
"""

import gzip
import re
import unicodedata
from pathlib import Path
from typing import IO, ClassVar

from .implicit import CollationElements, ImplicitRange, implicit_weight
from .trie import Trie

SortKey = tuple[int, ...]
CollationTrie = Trie[int, CollationElements]

DATA_DIR = Path(__file__).resolve().parent

COLL_ELEMENT_PATTERN = re.compile(
    r"""
    \[
    (?:\*|\.)
    ([0-9A-Fa-f]{4})
    \.
    ([0-9A-Fa-f]{4})
    \.
    ([0-9A-Fa-f]{4})
    (?:\.[0-9A-Fa-f]{4,5})?
    \]
    """,
    re.X,
)

# Parsed DUCET tables are shared across collator instances that load the same
# file, so constructing another ``Collator()`` is essentially free.
_TABLE_CACHE: dict[str, tuple[CollationTrie, list[ImplicitRange]]] = {}


def _open_ducet(path: Path) -> IO[str]:
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8")
    return path.open(encoding="utf-8")


def _load_table(path: Path) -> tuple[CollationTrie, list[ImplicitRange]]:
    cache_key = str(path)
    cached = _TABLE_CACHE.get(cache_key)
    if cached is not None:
        return cached

    table: CollationTrie = Trie()
    implicit_ranges: list[ImplicitRange] = []
    base_origin: dict[int, int] = {}

    with _open_ducet(path) as keys_file:
        for raw_line in keys_file:
            line = raw_line.split("#", 1)[0].rstrip()

            if not line or line.startswith("@version"):
                continue

            if line.startswith("@implicitweights"):
                ch_range, base_str = line[len("@implicitweights") :].split(";")
                range_start, range_end = ch_range.split("..")
                start = int(range_start, 16)
                base = int(base_str, 16)
                # Ranges sharing a base form one logical block; offsets are
                # measured from the first (lowest) range with that base.
                origin = base_origin.setdefault(base, start)
                implicit_ranges.append((start, int(range_end, 16), base, origin))
                continue

            a, b = line.split(";", 1)
            char_list = [int(hexstr, 16) for hexstr in a.split()]
            coll_elements: CollationElements = [
                [int(weight, 16) for weight in match.groups()]
                for match in COLL_ELEMENT_PATTERN.finditer(b.strip())
            ]
            table.add(char_list, coll_elements)

    result = (table, implicit_ranges)
    _TABLE_CACHE[cache_key] = result
    return result


class BaseCollator:
    UCA_VERSION: ClassVar[str] = ""

    def __init__(self, filename: str | Path | None = None) -> None:
        if filename is None:
            path = DATA_DIR / f"allkeys-{self.UCA_VERSION}.txt.gz"
        else:
            path = Path(filename)
        self.table, self.implicit_ranges = _load_table(path)

    def implicit_weight(self, cp: int) -> CollationElements:
        return implicit_weight(cp, self.implicit_ranges)

    def collation_elements(self, normalized_string: str) -> CollationElements:
        collation_elements: CollationElements = []

        code_points = self.build_lookup_key(normalized_string)
        i = 0
        while i < len(code_points):
            end, value = self.table.find_prefix_from(code_points, i)

            if value is not None:
                # discontiguous contraction (UCA S2.1.3): try to absorb a
                # following non-starter that is not blocked from the match S.
                last_class = None
                j = end
                while j < len(code_points):
                    combining_class = unicodedata.combining(chr(code_points[j]))
                    if combining_class == 0 or combining_class == last_class:
                        break
                    last_class = combining_class
                    candidate = code_points[i:end] + [code_points[j]]
                    cand_end, cand_value = self.table.find_prefix_from(candidate)
                    if cand_value is not None and cand_end == len(candidate):
                        value = cand_value
                        del code_points[j]
                        break
                    j += 1
            else:
                value = self.implicit_weight(code_points[i])
                end = i + 1

            collation_elements.extend(value)
            i = end

        return collation_elements

    def sort_key_from_collation_elements(
        self, collation_elements: CollationElements
    ) -> SortKey:
        sort_key: list[int] = []

        for level in range(4):
            if level:
                sort_key.append(0)  # level separator
            for element in collation_elements:
                if len(element) > level:
                    ce_l = element[level]
                    if ce_l:
                        sort_key.append(ce_l)

        return tuple(sort_key)

    def sort_key(self, string: str) -> SortKey:
        normalized_string = unicodedata.normalize("NFD", string)
        collation_elements = self.collation_elements(normalized_string)
        return self.sort_key_from_collation_elements(collation_elements)

    def build_lookup_key(self, text: str) -> list[int]:
        return [ord(ch) for ch in text]


_COLLATOR_REGISTRY: dict[str, type[BaseCollator]] = {}


def _register(cls: type[BaseCollator]) -> type[BaseCollator]:
    _COLLATOR_REGISTRY[cls.UCA_VERSION] = cls
    return cls


def _noncharacter_code_points() -> frozenset[int]:
    points: set[int] = set()
    for plane in range(17):
        base = plane << 16
        points.add(base + 0xFFFE)
        points.add(base + 0xFFFF)
    points.update(range(0xFDD0, 0xFDF0))
    return frozenset(points)


_NONCHARACTERS = _noncharacter_code_points()


@_register
class Collator_5_2_0(BaseCollator):
    UCA_VERSION = "5.2.0"

    def _valid_char(self, ch: str) -> bool:
        category = unicodedata.category(ch)
        if category == "Cs":
            return False
        if category != "Cn":
            return True
        return ord(ch) not in _NONCHARACTERS

    def build_lookup_key(self, text: str) -> list[int]:
        return [ord(ch) for ch in text if self._valid_char(ch)]


@_register
class Collator_6_3_0(BaseCollator):
    UCA_VERSION = "6.3.0"


@_register
class Collator_8_0_0(BaseCollator):
    UCA_VERSION = "8.0.0"


@_register
class Collator_9_0_0(BaseCollator):
    UCA_VERSION = "9.0.0"


@_register
class Collator_10_0_0(BaseCollator):
    UCA_VERSION = "10.0.0"


@_register
class Collator_13_0_0(BaseCollator):
    UCA_VERSION = "13.0.0"


@_register
class Collator_14_0_0(BaseCollator):
    UCA_VERSION = "14.0.0"


@_register
class Collator_15_0_0(BaseCollator):
    UCA_VERSION = "15.0.0"


@_register
class Collator_15_1_0(BaseCollator):
    UCA_VERSION = "15.1.0"


@_register
class Collator_16_0_0(BaseCollator):
    UCA_VERSION = "16.0.0"


@_register
class Collator_17_0_0(BaseCollator):
    UCA_VERSION = "17.0.0"


def _version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def available_versions() -> list[str]:
    """Return the bundled UCA versions, oldest first."""
    return sorted(_COLLATOR_REGISTRY, key=_version_key)


def select_collator(unidata_version: str | None = None) -> type[BaseCollator]:
    """Return the bundled collator best matching a Unicode version.

    Prefers an exact match on ``unidata_version`` (defaulting to the running
    interpreter's ``unicodedata.unidata_version``), otherwise the newest
    bundled version that is not newer than it.
    """
    if unidata_version is None:
        unidata_version = unicodedata.unidata_version

    exact = _COLLATOR_REGISTRY.get(unidata_version)
    if exact is not None:
        return exact

    runtime = _version_key(unidata_version)
    candidates = available_versions()
    not_newer = [v for v in candidates if _version_key(v) <= runtime]
    chosen = not_newer[-1] if not_newer else candidates[-1]
    return _COLLATOR_REGISTRY[chosen]


Collator = select_collator()
