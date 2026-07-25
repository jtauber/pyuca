"""Python implementation of the Unicode Collation Algorithm (UCA).

Usage example::

    from pyuca import Collator
    c = Collator()

    sorted_words = sorted(words, key=c.sort_key)

The default ``Collator`` matches the running interpreter's Unicode version
(``unicodedata.unidata_version``). To pin a specific UCA version, import it
directly, e.g. ``from pyuca.collator import Collator_16_0_0``.

``Collator`` can also take an optional filename for a custom collation element
table.
"""

from importlib.metadata import PackageNotFoundError, version

from .collator import Collator

try:
    __version__ = version("pyuca")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

__all__ = ["Collator", "__version__"]
