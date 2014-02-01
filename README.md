# pyuca: Python Unicode Collation Algorithm implementation

[![Build Status](https://travis-ci.org/jtauber/pyuca.png?branch=master)](https://travis-ci.org/jtauber/pyuca)
[![Coverage Status](https://coveralls.io/repos/jtauber/pyuca/badge.png?branch=master)](https://coveralls.io/r/jtauber/pyuca?branch=master)

This is a Python 3 implementation of the
[Unicode Collation Algorithm (UCA)](http://unicode.org/reports/tr10/). It
passes 100% of the UCA conformances tests for Unicode 6.3.0 with a
variable-weighting setting of Non-ignorable.

## What do you use it for?

In short, sorting non-English strings properly.

The core of the algorithm involves multi-level comparison. For example,
``café`` comes before ``caff`` because at the primary level, the accent is
ignored and the first word is treated as if it were ``cafe``. The secondary
level (which considers accents) only applies then to words that are equivalent
at the primary level.

The Unicode Collation Algorithm and pyuca also support contraction and
expansion. **Contraction** is where multiple letters are treated as a single
unit. In Spanish, ``ch`` is treated as a letter coming between ``c`` and ``d``
so that, for example, words beginning ``ch`` should sort after all other words
beginnings with ``c``. **Expansion** is where a single letter is treated as
though it were multiple letters. In German, ``ä`` is sorted as if it were
``ae``, i.e. after ``ad`` but before ``af``.

## How to use it

Here is how to use the ``pyuca`` module.

    pip install pyuca

Usage example:

    from pyuca import Collator
    c = Collator()

    sorted_words = sorted(words, key=c.sort_key)

``Collator`` takes an optional filename if you need to tailor the collation
for your specific language usage.

## License

Python code is made available under an MIT license (see `LICENSE`).
`allkeys.txt` is made available under the similar license defined in
`LICENSE-allkeys`.
