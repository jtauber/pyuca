import doctest

import pyuca.utils
from pyuca.utils import (
    format_collation_elements,
    format_sort_key,
    hexstrings2int,
    int2hexstrings,
)


def test_hexstrings2int():
    assert hexstrings2int(["0000", "0001", "FFFF"]) == [0, 1, 65535]


def test_int2hexstrings():
    assert int2hexstrings([0, 1, 65535]) == ["0000", "0001", "FFFF"]


def test_format_collation_elements():
    assert (
        format_collation_elements([[1, 2, 3], [4, 5]])
        == "[0001.0002.0003], [0004.0005]"
    )


def test_format_collation_elements_none():
    assert format_collation_elements(None) is None


def test_format_sort_key():
    assert format_sort_key([0, 1, 65535]) == "| 0001 FFFF"


def test_utils_doctests():
    results = doctest.testmod(pyuca.utils)
    assert results.failed == 0
