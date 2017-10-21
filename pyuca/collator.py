from __future__ import unicode_literals

import os.path
import re
import sys
import unicodedata
from io import open

from .trie import Trie
from .utils import hexstrings2int

try:
    chr = unichr
except NameError:
    pass

COLL_ELEMENT_PATTERN = re.compile(r"""
    \[
    (\*|\.)
    ([0-9A-Fa-f]{4})
    \.
    ([0-9A-Fa-f]{4})
    \.
    ([0-9A-Fa-f]{4})
    (?:\.[0-9A-Fa-f]{4,5})?
\]
""", re.X)


class BaseCollator(object):
    CJK_IDEOGRAPHS_8_0_0 = False
    CJK_IDEOGRAPHS_10_0_0 = False
    CJK_IDEOGRAPHS_EXT_A = True  # 3.0
    CJK_IDEOGRAPHS_EXT_B = True  # 3.1
    CJK_IDEOGRAPHS_EXT_C = True  # 5.2 (supposedly)
    CJK_IDEOGRAPHS_EXT_D = True  # 6.0
    CJK_IDEOGRAPHS_EXT_E = False  # 8.0
    CJK_IDEOGRAPHS_EXT_F = False  # 10.0

    def __init__(self, filename=None):
        if filename is None:
            filename = os.path.join(
                os.path.dirname(__file__),
                "allkeys-{0}.txt".format(self.UCA_VERSION))
        self.table = Trie()
        self.implicit_weights = []
        self.load(filename)

    def load(self, filename):
        with open(filename) as keys_file:
            for line in keys_file:
                line = line.split("#", 1)[0].rstrip()

                if not line or line.startswith("@version"):
                    continue

                if line.startswith("@implicitweights"):
                    ch_range, base = line[len("@implicitweights"):].split(";")
                    range_start, range_end = ch_range.split("..")
                    self.implicit_weights.append([
                        int(range_start, 16), int(range_end, 16), int(base, 16)
                    ])
                    continue

                a, b = line.split(";", 1)
                char_list = hexstrings2int(a.split())
                ce_with_var_tag_list = []
                for x in COLL_ELEMENT_PATTERN.finditer(b.strip()):
                    [v, l1w, l2w, l3w] = x.groups()
                    is_variable = {"*": True, ".": False}[v]
                    weights = [l1w, l2w, l3w]
                    ce_with_var_tag_list.append((is_variable,
                                                 hexstrings2int(weights)))
                self.table.add(char_list, ce_with_var_tag_list)

    def collation_elements(self, normalized_string, variable_weighting):
        """
        Produce the array of collation elements for a string from its NFD form.

        Reference algorithm: https://www.unicode.org/reports/tr10/tr10-36.html#Step_2
        """  # noqa: E501
        collation_elements = []

        lookup_key = self.build_lookup_key(normalized_string)
        while lookup_key:
            (S,  # S2.1
             value,  # S2.2
             lookup_key) = self.table.find_prefix(lookup_key)

            # handle non-starters
            # S2.1.1 ???

            last_class = None
            for i, C in enumerate(lookup_key):
                combining_class = unicodedata.combining(chr(C))
                if combining_class == 0 or combining_class == last_class:
                    break
                last_class = combining_class
                # S2.1.2 ???
                # C is a non-starter that is not blocked from S
                x, y, z = self.table.find_prefix(S + [C])
                if z == [] and y is not None:  # S2.1.3 ???
                    lookup_key = lookup_key[:i] + lookup_key[i + 1:]
                    value = y  # S2.2
                    break  # ???

            if not value:  # S2.2

                codepoint = lookup_key.pop(0)
                value = self.implicit_weight(codepoint)

            ce_with_var_tag_list = value  # S2.2

            ces = self.collation_elements_with_variable_weighting(ce_with_var_tag_list, variable_weighting)  # S2.3 # noqa: E501

            collation_elements.extend(ces)  # S2.4

            # S2.5

        return collation_elements

    def collation_elements_with_variable_weighting(self, ce_with_var_tag_list, vw):  # noqa: E501
        """
        Produce collation elements transforming variable elements
        according to the variable-weight setting.

        Reference algorithm: https://www.unicode.org/reports/tr10/tr10-36.html#Variable_Weighting
        """  # noqa: E501
        if vw == "non-ignorable":
            return [ce for (_, ce) in ce_with_var_tag_list]
        elif vw == "shifted":
            is_previous_variable = False
            ce_list = []
            for is_variable, ce in ce_with_var_tag_list:
                l1 = ce[0]
                l2 = ce[1]  # XXX How does spec guarantee this is defined?
                l3 = ce[2]  # XXX How does spec guarantee this is defined?
                if (l1 == 0) and (l2 == 0) and (l3 == 0):
                    weighted_ce = [0, 0, 0, 0]
                elif (l1 == 0) and (l3 != 0) and is_previous_variable:
                    weighted_ce = [0, 0, 0, 0]
                elif (l1 != 0) and is_variable:
                    weighted_ce = [0, 0, 0, l1]
                elif (l1 == 0) and (l3 != 0) and (not is_previous_variable):
                    weighted_ce = [l1, l2, l3, int("FFFF", 16)]
                elif (l1 != 0) and (not is_variable):
                    weighted_ce = [l1, l2, l3, int("FFFF", 16)]
                ce_list.append(weighted_ce)
                is_previous_variable = is_variable
            return ce_list
        else:
            raise NotImplementedError(vw)

    def sort_key_from_collation_elements(self, collation_elements,
                                         max_level=4, level_sep=0):
        """
        Produce the sort key for a string from its array of collation elements.

        Reference algorithm: https://www.unicode.org/reports/tr10/tr10-36.html#Step_3
        """  # noqa: E501
        sort_key = []

        available_levels = max([len(ce) for ce in collation_elements])
        for level in range(min(max_level, available_levels)):  # S3.1
            if level > 0:  # S3.2
                sort_key.append(level_sep)

            # Assumption: collation element table is forwards (as
            # opposed to backwards) at this level.  This entails
            # following branch S3.3 of the algorithm and ignoring
            # branch S3.6 (and its children steps S3.7 S3.8 S3.9).
            for ce in collation_elements:  # S3.4

                # Not appending anything for collation elements
                # without weight at this level is equivalent to
                # defaulting such weight to zero - see S3.5.
                if len(ce) > level:
                    ce_l = ce[level]
                    if ce_l > 0:  # S3.5
                        sort_key.append(ce_l)

        # According to the algorithm at
        # https://www.unicode.org/reports/tr10/tr10-36.html#Step_3 the
        # sort key does not have to end with a level separator.  See
        # also examples at
        # https://www.unicode.org/reports/tr10/tr10-36.html#Array_To_Sort_Key_Table
        # and
        # https://www.unicode.org/reports/tr10/tr10-36.html#Comparison_Of_Sort_Keys_Table
        #
        # However the conformance tests at
        # https://www.unicode.org/Public/UCA/10.0.0/CollationTest.html
        # include in (non-normative) comments "a representation of the
        # sort key" always ending with "|]" where the vertical bar
        # stands for "the ZERO separator".
        #
        # Append a final unnecessary level separator for the sake of
        # readability following the comments in the conformance tests.
        # This entails unnecessary additional memory usage.
        sort_key.append(level_sep)

        # Assumption: no deterministic (sometimes called stable or
        # semi-stable) comparison required.  This entails skipping
        # step S3.10 of the algorithm.

        return tuple(sort_key)

    def sort_key(self, string, variable_weighting="non-ignorable"):
        """
        Produce the sort key for the input string.

        Reference algorithm: https://www.unicode.org/reports/tr10/tr10-36.html#Main_Algorithm
        """  # noqa: E501
        normalized_string = unicodedata.normalize("NFD", string)  # S1.1
        collation_elements = self.collation_elements(normalized_string,
                                                     variable_weighting)  # S2
        return self.sort_key_from_collation_elements(collation_elements)  # S3

    def implicit_weight(self, cp):
        if (
            (unicodedata.category(chr(cp)) != "Cn") and (
                0x4E00 <= cp <= 0x9FCC or
                (self.CJK_IDEOGRAPHS_8_0_0 and 0x9FCD <= cp <= 0x9FD5) or
                (self.CJK_IDEOGRAPHS_10_0_0 and 0x9FD6 <= cp <= 0x9FEA) or
                cp in [
                    0xFA0E, 0xFA0F, 0xFA11, 0xFA13, 0xFA14, 0xFA1F,
                    0xFA21, 0xFA23, 0xFA24, 0xFA27, 0xFA28, 0xFA29,
                ]
            )
        ):
            base = 0xFB40
            aaaa = base + (cp >> 15)
            bbbb = (cp & 0x7FFF) | 0x8000
        elif (
            (unicodedata.category(chr(cp)) != "Cn") and (
                (self.CJK_IDEOGRAPHS_EXT_A and 0x3400 <= cp <= 0x4DB5) or
                (self.CJK_IDEOGRAPHS_EXT_B and 0x20000 <= cp <= 0x2A6D6) or
                (self.CJK_IDEOGRAPHS_EXT_C and 0x2A700 <= cp <= 0x2B734) or
                (self.CJK_IDEOGRAPHS_EXT_D and 0x2B740 <= cp <= 0x2B81D) or
                (self.CJK_IDEOGRAPHS_EXT_E and 0x2B820 <= cp <= 0x2CEAF) or
                (self.CJK_IDEOGRAPHS_EXT_F and 0x2CEB0 <= cp <= 0x2EBE0)
            )
        ):
            base = 0xFB80
            aaaa = base + (cp >> 15)
            bbbb = (cp & 0x7FFF) | 0x8000
        else:
            aaaa = None
            for (start, end, base) in self.implicit_weights:
                if start <= cp <= end:
                    aaaa = base
                    bbbb = (cp - start) | 0x8000
                    break
            if aaaa is None:
                base = 0xFBC0
                aaaa = base + (cp >> 15)
                bbbb = (cp & 0x7FFF) | 0x8000

        collation_elements = [[aaaa, 0x0020, 0x002], [bbbb, 0x0000, 0x0000]]
        is_variable = False
        return [(is_variable, ce) for ce in collation_elements]

    def build_lookup_key(self, text):
        return [ord(ch) for ch in text]


class Collator_6_3_0(BaseCollator):
    UCA_VERSION = "6.3.0"


class Collator_8_0_0(BaseCollator):
    UCA_VERSION = "8.0.0"
    CJK_IDEOGRAPHS_8_0_0 = True
    CJK_IDEOGRAPHS_EXT_E = True


class Collator_9_0_0(BaseCollator):
    UCA_VERSION = "9.0.0"
    CJK_IDEOGRAPHS_8_0_0 = True
    CJK_IDEOGRAPHS_EXT_E = True


class Collator_10_0_0(BaseCollator):
    UCA_VERSION = "10.0.0"
    CJK_IDEOGRAPHS_8_0_0 = True
    CJK_IDEOGRAPHS_10_0_0 = True
    CJK_IDEOGRAPHS_EXT_E = True
    CJK_IDEOGRAPHS_EXT_F = True


class Collator_5_2_0(BaseCollator):
    UCA_VERSION = "5.2.0"
    # Supposedly, extension C *was* introduced in 5.2.0, but the tests show
    # otherwise. Treat the tests as king.
    CJK_IDEOGRAPHS_EXT_C = False
    CJK_IDEOGRAPHS_EXT_D = False

    non_char_code_points = []
    for i in range(17):
        base = i << 16
        non_char_code_points.append(base + 0xFFFE)
        non_char_code_points.append(base + 0xFFFF)
    for i in range(32):
        non_char_code_points.append(0xFDD0 + i)

    def _valid_char(self, ch):
        category = unicodedata.category(ch)
        if category == "Cs":
            return False
        if category != "Cn":
            return True
        return ord(ch) not in self.non_char_code_points

    def build_lookup_key(self, text):
        return [ord(ch) for ch in text if self._valid_char(ch)]


if sys.version_info < (3,):
    Collator = Collator_5_2_0
elif sys.version_info[:2] == (3, 5):
    Collator = Collator_8_0_0
elif sys.version_info[:2] >= (3, 6):
    Collator = Collator_9_0_0
else:
    Collator = Collator_6_3_0
