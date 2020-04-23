"""
This is a Python implementation of the Unicode Collation Algorithm (UCA). It
passes 100% of the UCA conformance tests for Unicode 8.0.0 (Python 3.5+),
Unicode 9.0.0 (Python 3.6+), and Unicode 10.0.0 (Python 3.7+) with a
variable-weighting setting of Non-ignorable.


Usage example:

    from pyuca import Collator
    c = Collator()

    assert sorted(["cafe", "caff", "café"]) == ["cafe", "caff", "café"]
    assert sorted(["cafe", "caff", "café"], key=c.sort_key) == ["cafe", "café", "caff"]

``Collator`` can also take an optional filename for specifying a custom
collation element table.
"""

from .collator import Collator  # noqa
