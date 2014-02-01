import os.path
import re

from .trie import Trie
from .utils import hexstrings2int


COLL_ELEMENT_PATTERN = r"""
    \[
    (\*|\.)
    ([0-9A-Fa-f]{4})
    \.
    ([0-9A-Fa-f]{4})
    \.
    ([0-9A-Fa-f]{4})
    (?:\.([0-9A-Fa-f]{4}))?
\]
"""


class Collator:

    def __init__(self, filename=None):

        if filename is None:
            filename = os.path.join(os.path.dirname(__file__), "allkeys.txt")
        self.table = Trie()
        self.load(filename)

    def load(self, filename):
        with open(filename) as keys_file:
            for line in keys_file:
                line = line.split("#")[0].split("%")[0].strip()

                if not line:
                    continue

                if line.startswith("@version"):
                    pass
                else:
                    a, b = line.split(";")
                    char_list = hexstrings2int(a.split())
                    coll_elements = []
                    for x in re.finditer(COLL_ELEMENT_PATTERN, b.strip(), re.X):
                        alt, weight1, weight2, weight3, weight4 = x.groups()
                        weights = [weight1, weight2, weight3]
                        if weight4:
                            weights.append(weight4)
                        coll_elements.append(hexstrings2int(weights))
                    self.table.add(char_list, coll_elements)

    def collation_elements(self, string):
        collation_elements = []

        lookup_key = [ord(ch) for ch in string]
        while lookup_key:
            value, lookup_key = self.table.find_prefix(lookup_key)
            if not value:
                # Calculate implicit weighting for CJK Ideographs
                # http://www.unicode.org/reports/tr10/#Implicit_Weights
                key = lookup_key[0]
                value = [
                    (0xFB40 + (key >> 15), 0x0020, 0x0002, 0x0001),
                    ((key & 0x7FFF) | 0x8000, 0x0000, 0x0000, 0x0000)
                ]
                lookup_key = lookup_key[1:]
            collation_elements.extend(value)

        return collation_elements

    def sort_key_from_collation_elements(self, collation_elements):
        sort_key = []

        for level in range(4):
            if level:
                sort_key.append(0)  # level separator
            for element in collation_elements:
                if len(element) > level:
                    ce_l = element[level]
                    if ce_l:
                        sort_key.append(ce_l)

        return tuple(sort_key)

    def sort_key(self, string):

        collation_elements = self.collation_elements(string)
        return self.sort_key_from_collation_elements(collation_elements)
