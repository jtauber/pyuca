"""
Preliminary implementation of the Unicode Collation Algorithm.

This only implements the simple parts of the algorithm but I have successfully
tested it using the Default Unicode Collation Element Table (DUCET) to collate
Ancient Greek correctly.

Usage example:

    from pyuca import Collator
    c = Collator()

    sorted_words = sorted(words, key=c.sort_key)

Collator can also take an optional filename for specifying a custom collation
element table.
"""

from collator import Collator
