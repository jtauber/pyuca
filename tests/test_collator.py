import textwrap

from pyuca import Collator
from pyuca.collator import (
    Collator_5_2_0,
    available_versions,
    select_collator,
)

# --- default collator behaviour -------------------------------------------


def test_core_han_sort_key():
    # U+4E00 is core Han on every Unicode version -> implicit 0xFB40 weights.
    key = Collator().sort_key("一")
    assert key[:2] == (0xFB40, 0xCE00)


def test_repeated_instantiation_shares_table():
    # The module-level cache means a second Collator() reuses the parsed trie.
    assert Collator().table is Collator().table


# --- version selection -----------------------------------------------------


def test_exact_version_match():
    assert select_collator("16.0.0").UCA_VERSION == "16.0.0"


def test_between_versions_picks_newest_not_newer():
    # A hypothetical runtime on Unicode 11/12 gets the newest bundled <= it.
    assert select_collator("11.0.0").UCA_VERSION == "10.0.0"


def test_newer_than_all_picks_latest():
    assert select_collator("99.0.0").UCA_VERSION == "17.0.0"


def test_older_than_all_falls_back_to_latest():
    assert select_collator("1.0.0").UCA_VERSION == "17.0.0"


def test_available_versions_sorted_numerically():
    versions = available_versions()
    # Guards against lexical sorting ("10.0.0" < "9.0.0").
    assert versions.index("9.0.0") < versions.index("10.0.0")
    assert versions[-1] == "17.0.0"


# --- Collator_5_2_0 code-point filtering -----------------------------------


def test_5_2_0_filters_noncharacters_and_surrogates():
    c = Collator_5_2_0()
    assert c.build_lookup_key("ab") == [0x61, 0x62]
    assert c.build_lookup_key("a﷐b") == [0x61, 0x62]  # noncharacter dropped
    assert c.build_lookup_key("a\ud800b") == [0x61, 0x62]  # surrogate dropped


# --- custom collation element table (plain-text path) ----------------------

_CUSTOM_DUCET = textwrap.dedent(
    """\
    # a tiny custom collation element table
    @version 99.0.0
    0061 ; [.0209.0020.0002]  # a
    0062 ; [.020A.0020.0002]  # b
    0063 0068 ; [.0250.0020.0002]  # ch as a single unit
    @implicitweights 17000..18AFF; FB00  # a made-up implicit block
    """
)


def test_custom_table(tmp_path):
    path = tmp_path / "custom-allkeys.txt"
    path.write_text(_CUSTOM_DUCET, encoding="utf-8")
    c = Collator(filename=str(path))

    assert c.sort_key("a") < c.sort_key("b")
    # "ch" contracts to one collation element with primary 0x0250.
    assert c.sort_key("ch")[0] == 0x0250
    # code point inside the custom @implicitweights block uses base 0xFB00.
    assert c.sort_key("\U00017000")[0] == 0xFB00


# A table with an "a + combining grave" contraction, used to exercise
# discontiguous contraction: an intervening combining mark of a lower combining
# class (U+0323, ccc 220) does not block U+0300 (ccc 230) from contracting.
_DISCONTIGUOUS_DUCET = textwrap.dedent(
    """\
    @version 99.0.0
    0061 ; [.0209.0020.0002]  # a
    0300 ; [.0000.0035.0002]  # combining grave accent (ccc 230)
    0323 ; [.0000.0038.0002]  # combining dot below (ccc 220)
    0061 0300 ; [.0209.0021.0002]  # a-grave as one unit
    """
)


def test_direct_contraction(tmp_path):
    """a + grave contracts to one unit (contiguous case)."""
    path = tmp_path / "contraction.txt"
    path.write_text(_DISCONTIGUOUS_DUCET, encoding="utf-8")
    c = Collator(filename=str(path))
    # "a" + U+0300 -> single CE [.0209.0021.0002].
    assert c.sort_key("à") == (0x0209, 0x0000, 0x0021, 0x0000, 0x0002, 0x0000)


def test_discontiguous_contraction(tmp_path):
    path = tmp_path / "discontiguous.txt"
    path.write_text(_DISCONTIGUOUS_DUCET, encoding="utf-8")
    c = Collator(filename=str(path))

    # "a" + dot-below (ccc 220) + grave (ccc 230): the grave contracts into
    # "a+grave" across the non-blocking dot-below, which is then weighted on its
    # own -> CEs [.0209.0021.0002] then [.0000.0038.0002].
    assert c.sort_key("ạ̀") == (
        0x0209,
        0x0000,
        0x0021,
        0x0038,
        0x0000,
        0x0002,
        0x0002,
        0x0000,
    )
