# coding: utf8
from __future__ import unicode_literals

import sys
import unittest

PYTHON3 = sys.version_info >= (3,)
V8_0_0 = sys.version_info >= (3, 5)
V10_0_0 = sys.version_info >= (3, 7)


class SmokeTest(unittest.TestCase):

    def test_cafe(self):
        from pyuca import Collator
        c = Collator()

        self.assertEqual(
            sorted(["cafe", "caff", "café"]),
            ["cafe", "caff", "café"]
        )
        self.assertEqual(
            sorted(["cafe", "caff", "café"], key=c.sort_key),
            ["cafe", "café", "caff"]
        )


class UtilsTest(unittest.TestCase):

    def test_hexstrings2int(self):
        from pyuca.utils import hexstrings2int
        self.assertEqual(
            hexstrings2int(["0000", "0001", "FFFF"]),
            [0, 1, 65535]
        )

    def test_int2hexstrings(self):
        from pyuca.utils import int2hexstrings
        self.assertEqual(
            int2hexstrings([0, 1, 65535]),
            ["0000", "0001", "FFFF"]
        )

    def test_format_collation_elements(self):
        from pyuca.utils import format_collation_elements
        self.assertEqual(
            format_collation_elements([[1, 2, 3], [4, 5]]),
            "[0001.0002.0003], [0004.0005]"
        )

    def test_format_collation_elements_none(self):
        from pyuca.utils import format_collation_elements
        self.assertEqual(
            format_collation_elements(None),
            None
        )

    def test_format_sort_key(self):
        from pyuca.utils import format_sort_key
        self.assertEqual(
            format_sort_key([0, 1, 65535]),
            "| 0001 FFFF"
        )


class TrieTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        from pyuca.trie import Trie
        super(TrieTest, self).__init__(*args, **kwargs)
        self.t = Trie()

    def test_1(self):
        self.t.add("foo", "bar")
        self.assertEqual(self.t.find_prefix("fo"), ("", None, "fo"))
        self.assertEqual(self.t.find_prefix("foo"), ("foo", "bar", ""))
        self.assertEqual(self.t.find_prefix("food"), ("foo", "bar", "d"))

    def test_2(self):
        self.t.add("a", "yes")
        self.t.add("abc", "yes")
        self.assertEqual(self.t.find_prefix("abdc"), ("a", "yes", "bdc"))


class FromFullTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        from pyuca import Collator
        super(FromFullTest, self).__init__(*args, **kwargs)
        self.c = Collator()
        (0, 74, 33, 0, 2, 2, 0)

    @unittest.skipIf(not PYTHON3, "only matches Python 3's UCA version")
    def test_1(self):
        self.assertEqual(
            self.c.sort_key("\u0332\u0334"),
            (0x0000, 0x004A, 0x0021, 0x0000, 0x0002, 0x0002, 0x0000)
        )

    @unittest.skipIf(not PYTHON3, "only matches Python 3's UCA version")
    @unittest.skipIf(V8_0_0, "not for UCA version 8.0.0")
    @unittest.skipIf(V10_0_0, "not for UCA version 10.0.0")
    def test_2(self):
        self.assertEqual(
            self.c.sort_key("\u0430\u0306\u0334"),
            (0x1991, 0x0000, 0x0020, 0x004A, 0x0000, 0x0002, 0x0002, 0x0000)
        )

    @unittest.skipIf(not PYTHON3, "only matches Python 3's UCA version")
    @unittest.skipIf(V8_0_0, "not for UCA version 8.0.0")
    @unittest.skipIf(V10_0_0, "not for UCA version 10.0.0")
    def test_3(self):
        self.assertEqual(
            self.c.sort_key("\u0FB2\u0F71\u0001\u0F80\u0061"),
            (0x2571, 0x2587, 0x258A, 0x15EB, 0x0000, 0x0020, 0x0020, 0x0020,
                0x0020, 0x0000, 0x0002, 0x0002, 0x0002, 0x0002, 0x0000)
        )

    @unittest.skipIf(not PYTHON3, "only matches Python 3's UCA version")
    @unittest.skipIf(V8_0_0, "not for UCA version 8.0.0")
    @unittest.skipIf(V10_0_0, "not for UCA version 10.0.0")
    def test_4(self):
        self.assertEqual(
            self.c.sort_key("\u4E00\u0021"),
            (0xFB40, 0xCE00, 0x025D, 0x0000, 0x0020,
                0x0020, 0x0000, 0x0002, 0x0002, 0x0000)
        )

    @unittest.skipIf(not PYTHON3, "only matches Python 3's UCA version")
    @unittest.skipIf(V8_0_0, "not for UCA version 8.0.0")
    @unittest.skipIf(V10_0_0, "not for UCA version 10.0.0")
    def test_5(self):
        self.assertEqual(
            self.c.sort_key("\u3400\u0021"),
            (0xFB80, 0xB400, 0x025D, 0x0000, 0x0020,
                0x0020, 0x0000, 0x0002, 0x0002, 0x0000)
        )

    @unittest.skipIf(PYTHON3, "only matches the older Python 2's UCA version")
    def test_1_old(self):
        self.assertEqual(
            self.c.sort_key("\u0332\u0334"),
            (0x0000, 0x007C, 0x0021, 0x0000, 0x0002, 0x0002, 0x0000)
        )

    @unittest.skipIf(PYTHON3, "only matches the older Python 2's UCA version")
    def test_2_old(self):
        self.assertEqual(
            self.c.sort_key("\u0430\u0306\u0334"),
            (0x15B0, 0x0000, 0x0020, 0x007C, 0x0000, 0x0002, 0x0002, 0x0000)
        )

    @unittest.skipIf(PYTHON3, "only matches the older Python 2's UCA version")
    def test_3_old(self):
        self.assertEqual(
            self.c.sort_key("\u0FB2\u0F71\u0001\u0F80\u0061"),
            (0x205B, 0x206D, 0x2070, 0x120F, 0x0000, 0x0020, 0x0020, 0x0020,
                0x0020, 0x0000, 0x0002, 0x0002, 0x0002, 0x0002, 0x0000)
        )

    @unittest.skipIf(PYTHON3, "only matches the older Python 2's UCA version")
    def test_4_old(self):
        self.assertEqual(
            self.c.sort_key("\u4E00\u0021"),
            (0xFB40, 0xCE00, 0x026E, 0x0000, 0x0020,
                0x0020, 0x0000, 0x0002, 0x0002, 0x0000)
        )

    @unittest.skipIf(PYTHON3, "only matches the older Python 2's UCA version")
    def test_5_old(self):
        self.assertEqual(
            self.c.sort_key("\u3400\u0021"),
            (0xFB80, 0xB400, 0x026E, 0x0000, 0x0020,
                0x0020, 0x0000, 0x0002, 0x0002, 0x0000)
        )


class FromFullTestV8_0_0(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        from pyuca.collator import Collator_8_0_0
        super(FromFullTestV8_0_0, self).__init__(*args, **kwargs)
        self.c = Collator_8_0_0()

    @unittest.skipIf(not V8_0_0, "only matches UCA version 8.0.0")
    def test_1(self):
        from pyuca.utils import format_sort_key
        self.assertEqual(
            format_sort_key(self.c.sort_key("\u9FD5\u0062")),
            "FB41 9FD5 1BDB | 0020 0020 | 0002 0002 |",
        )

    @unittest.skipIf(not V8_0_0, "only matches UCA version 8.0.0")
    def test_2(self):
        from pyuca.utils import format_sort_key
        self.assertEqual(
            format_sort_key(self.c.sort_key("\U0002CEA1\u0062")),
            "FB85 CEA1 1BDB | 0020 0020 | 0002 0002 |",
        )

    @unittest.skipIf(not V8_0_0, "only matches UCA version 8.0.0")
    def test_3(self):
        from pyuca.utils import format_sort_key
        self.assertEqual(
            format_sort_key(self.c.sort_key("\U0002B81E\u0062")),
            "FBC5 B81E 1BDB | 0020 0020 | 0002 0002 |",
        )

    @unittest.skipIf(not V8_0_0, "only matches UCA version 8.0.0")
    def test_4(self):
        from pyuca.utils import format_sort_key
        self.assertEqual(
            format_sort_key(self.c.sort_key("\U0002CEA2\u0021")),
            "FBC5 CEA2 025F | 0020 0020 | 0002 0002 |",
        )


class FromFullTestV10_0_0(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        from pyuca.collator import Collator_10_0_0
        super(FromFullTestV10_0_0, self).__init__(*args, **kwargs)
        self.c = Collator_10_0_0()

    @unittest.skipIf(not V10_0_0, "only matches UCA version 10.0.0")
    def test_1(self):
        from pyuca.utils import format_sort_key
        self.assertEqual(
            format_sort_key(self.c.sort_key("\u1DF6\u0334")),
            "| 004A 0033 | 0002 0002 |",
        )

    @unittest.skipIf(not V10_0_0, "only matches UCA version 10.0.0")
    def test_2(self):
        from pyuca.utils import format_sort_key
        self.assertEqual(
            format_sort_key(self.c.sort_key("\u9FEA\u0062")),
            "FB41 9FEA 1CC6 | 0020 0020 | 0002 0002 |",
        )


if __name__ == "__main__":
    unittest.main()
