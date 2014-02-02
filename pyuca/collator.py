import os.path
import re
import unicodedata

from .trie import Trie
from .utils import hexstrings2int


COLL_ELEMENT_PATTERN = re.compile(r"""
    \[
    (\*|\.)
    ([0-9A-Fa-f]{4})
    \.
    ([0-9A-Fa-f]{4})
    \.
    ([0-9A-Fa-f]{4})
    (?:\.([0-9A-Fa-f]{4}))?
\]
""", re.X)


class Collator:

    def __init__(self, ce_table_filename=None, **custom_settings):

        if ce_table_filename is None:
            ce_table_filename = os.path.join(
                os.path.dirname(__file__),
                "allkeys.txt"
            )

        settings = {
            "strength": "tertiary",
            "alternate": "non-ignorable",
            "backwards": "off",
            "normalization": "on",
        }
        settings.update(custom_settings)

        self.max_level = {
            "primary": 1,
            "secondary": 2,
            "tertiary": 3,
            "quaternary": 4,
            "identical": 5
        }[settings["strength"]]

        self.normalization = {
            "on": True,
            "off": False,
        }[settings["normalization"]]

        self.backwards_levels = {
            "on": [1],
            "off": [],
        }[settings["backwards"]]

        self.table = Trie()
        self.load(ce_table_filename)

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
                    for x in COLL_ELEMENT_PATTERN.finditer(b.strip()):
                        alt, weight1, weight2, weight3, weight4 = x.groups()
                        weights = [weight1, weight2, weight3]
                        if weight4:
                            weights.append(weight4)
                        coll_elements.append(hexstrings2int(weights))
                    self.table.add(char_list, coll_elements)

    def collation_elements(self, normalized_string):
        collation_elements = []

        lookup_key = [ord(ch) for ch in normalized_string]
        while lookup_key:
            S, value, lookup_key = self.table.find_prefix(lookup_key)

            # handle non-starters

            last_class = None
            for i, C in enumerate(lookup_key):
                combining_class = unicodedata.combining(chr(C))
                if combining_class == 0 or combining_class == last_class:
                    break
                last_class = combining_class
                # C is a non-starter that is not blocked from S
                x, y, z = self.table.find_prefix(S + [C])
                if z == [] and y is not None:
                    lookup_key = lookup_key[:i] + lookup_key[i + 1:]
                    value = y
                    break  # ???

            if not value:

                # implicit weighting

                CP = lookup_key.pop(0)

                if 0x4E00 <= CP <= 0x9FCC or CP in [
                        0xFA0E, 0xFA0F, 0xFA11, 0xFA13, 0xFA14, 0xFA1F,
                        0xFA21, 0xFA23, 0xFA24, 0xFA27, 0xFA28, 0xFA29]:
                    BASE = 0xFB40
                elif (0x3400 <= CP <= 0x4DB5 or 0x20000 <= CP <= 0x2A6D6 or
                        0x2A700 <= CP <= 0x2B734 or 0x2B740 <= CP <= 0x2B81D):
                    BASE = 0xFB80
                else:
                    BASE = 0xFBC0

                AAAA = BASE + (CP >> 15)
                BBBB = (CP & 0x7FFF) | 0x8000
                value = [[AAAA, 0x0020, 0x002], [BBBB, 0x0000, 0x0000]]

            collation_elements.extend(value)

        return collation_elements

    def sort_key_from_collation_elements(self, collation_elements):
        sort_key = []

        for level in range(self.max_level):
            if level:
                sort_key.append(0)  # level separator
            new_keys = []
            for element in collation_elements:
                if len(element) > level:
                    ce_l = element[level]
                    if ce_l:
                        new_keys.append(ce_l)
            if level in self.backwards_levels:
                new_keys.reverse()
            sort_key.extend(new_keys)

        return tuple(sort_key)

    def sort_key(self, string):
        if self.normalization:
            normalized_string = unicodedata.normalize("NFD", string)
        else:
            normalized_string = string
        collation_elements = self.collation_elements(normalized_string)
        return self.sort_key_from_collation_elements(collation_elements)
