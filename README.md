# pyuca: Python Unicode Collation Algorithm implementation

[![CI](https://github.com/jtauber/pyuca/actions/workflows/ci.yml/badge.svg)](https://github.com/jtauber/pyuca/actions/workflows/ci.yml)
![MIT License](https://img.shields.io/badge/license-MIT-brightgreen.svg)
[![DOI](https://zenodo.org/badge/3769/jtauber/pyuca.svg)](https://zenodo.org/badge/latestdoi/3769/jtauber/pyuca)
[![JOSS](https://joss.theoj.org/papers/10.21105/joss.00021/status.svg)](https://joss.theoj.org/papers/10.21105/joss.00021)

This is a Python implementation of the
[Unicode Collation Algorithm (UCA)](https://www.unicode.org/reports/tr10/). It
passes 100% of the UCA conformance tests for every bundled Unicode version
(5.2.0 through 17.0.0) with a variable-weighting setting of Non-ignorable, when
run on an interpreter whose Unicode version matches (see *Versioning* below).

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

Requires Python 3.11+.

    pip install pyuca

Usage example:

    from pyuca import Collator
    c = Collator()

    assert sorted(["cafe", "caff", "café"]) == ["cafe", "caff", "café"]
    assert sorted(["cafe", "caff", "café"], key=c.sort_key) == ["cafe", "café", "caff"]

``Collator`` can also take an optional filename for specifying a custom
collation element table (either a plain ``allkeys.txt`` or a gzipped one).

## Versioning

`sort_key` relies on the standard library's `unicodedata` for NFD
normalization, so a collation is only correct when the DUCET table matches the
interpreter's Unicode version. `from pyuca import Collator` therefore selects
the bundled table matching `unicodedata.unidata_version` automatically:

| Python | Unicode | Collator selected |
| ------ | ------- | ----------------- |
| 3.11   | 14.0.0  | `Collator_14_0_0` |
| 3.12   | 15.0.0  | `Collator_15_0_0` |
| 3.13   | 15.1.0  | `Collator_15_1_0` |
| 3.14   | 16.0.0  | `Collator_16_0_0` |

To pin a specific version regardless of the interpreter, import it directly:

    from pyuca.collator import Collator_16_0_0
    c = Collator_16_0_0()

Bundled tables (`Collator_5_2_0`, `Collator_6_3_0`, `Collator_8_0_0`,
`Collator_9_0_0`, `Collator_10_0_0`, `Collator_13_0_0` … `Collator_17_0_0`)
remain importable for reproducibility; `17.0.0` is included ahead of a CPython
release that ships Unicode 17.

> **Upgrading from 1.x?** 2.0 drops Python 2 and no longer picks the collator
> from `sys.version_info`. On modern Pythons the default previously resolved to
> UCA 9.0.0 (2016); it now tracks the runtime's Unicode version, so sort keys
> for characters added since then will differ.

## How to cite it

Tauber, J. K. (2016). pyuca: a Python implementation of the Unicode Collation Algorithm. The Journal of Open Source Software. DOI: 10.21105/joss.00021

## License

Python code is made available under an MIT license (see `LICENSE`).
`allkeys.txt` is made available under the similar license defined in
`LICENSE-allkeys`.

## Contacting the Developer

If you have any problems, questions or suggestions, it's best to file an issue
on GitHub although you can also contact me at jtauber@jtauber.com.

For more of my work on linguistics and Ancient Greek, see
<http://jktauber.com/>.
