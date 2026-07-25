# Changelog

## 2.0.0 (unreleased)

A modernization release. **Breaking:** requires Python 3.11+ and the default
`Collator` now tracks the interpreter's Unicode version, so sort keys may differ
from 1.x on modern Pythons (see the first bug fix below).

### Unicode data

- Added DUCET tables and Non-ignorable conformance suites for Unicode 13.0.0,
  14.0.0, 15.0.0, 15.1.0, 16.0.0 and 17.0.0 (previously topped out at 10.0.0).
- Tables are now stored gzipped; `scripts/fetch_ducet.py` regenerates them from
  unicode.org.

### Bugs fixed

- **Default collator ignored the runtime's Unicode version.** The default was
  chosen from `sys.version_info` via a branch that stopped at Python 3.6, so
  Python 3.7–3.14 all silently used **UCA 9.0.0** (2016) even though their
  `unicodedata` is 14.0–16.0. Selection is now driven by
  `unicodedata.unidata_version`, which is also the value `sort_key` normalizes
  against.
- **Falsy-value confusion in the trie / element lookup.** `Trie.find_prefix`
  and `collation_elements` tested collation values for truthiness rather than
  `is not None`, which would misroute a legitimately empty element list to
  implicit weighting. Now compared against `None`.
- **Discontiguous-contraction loop could fail to terminate** for a leading
  unmatched non-starter. The contraction search is now guarded on an actual
  prefix match, matching the algorithm's intent and guaranteeing progress.
- Minor: `implicit_weight` no longer computes `unicodedata.category` twice, and
  `Collator_5_2_0` no longer leaks loop variables into the class namespace.

### Performance

- **Parsed DUCET tables are cached per file.** Constructing a second
  `Collator()` dropped from ~52 ms to ~1.6 µs (the ~40 ms one-time parse is
  shared across all instances loading the same table).
- **`collation_elements` is now O(n).** Replaced `list.pop(0)` and per-step
  slicing with an index cursor. Sorting keys for long strings is ~5× faster
  (e.g. 4000 combining marks 7.7 ms → 1.6 ms) and no longer quadratic.

### Tooling

- Packaging moved to `pyproject.toml` + hatchling + uv; `setup.py`,
  `setup.cfg`, `tox.ini`, `.travis.yml` and `MANIFEST.in` removed.
- Tests migrated to pytest with a parametrized conformance suite; 100% coverage
  is enforced.
- Added full type hints, a `py.typed` marker, and pyright (standard mode).
- Replaced flake8 with ruff; CI moved from Travis to GitHub Actions
  (Python 3.11–3.14).

### Known limitations

- Only the Non-ignorable variable-weighting setting is implemented. The Shifted
  conformance fixtures are bundled but not yet exercised.
- A bundled version's conformance is only guaranteed on an interpreter whose
  `unicodedata` matches it. `Collator_17_0_0` is provided ahead of a CPython
  release shipping Unicode 17.
