from unittest import TestCase, main


class SmokeTest(TestCase):

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


class UtilsTest(TestCase):

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

    def test_display_collation_elements(self):
        from pyuca.utils import display_collation_elements
        self.assertEqual(
            display_collation_elements([[1, 2, 3], [4, 5]]),
            "[0001.0002.0003], [0004.0005]"
        )

    def test_display_collation_elements_none(self):
        from pyuca.utils import display_collation_elements
        self.assertEqual(
            display_collation_elements(None),
            None
        )

    def test_display_sort_key(self):
        from pyuca.utils import display_sort_key
        self.assertEqual(
            display_sort_key([0, 1, 65535]),
            "| 0001 FFFF"
        )


class TrieTest(TestCase):

    def setUp(self):
        from pyuca.trie import Trie
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


class FromFullTest(TestCase):

    def setUp(self):
        from pyuca import Collator
        self.c = Collator()

    def test_1(self):
        self.assertEqual(
            self.c.sort_key("\u0332\u0334"),
            (0x0000, 0x004A, 0x0021, 0x0000, 0x0002, 0x0002, 0x0000)
        )

    def test_2(self):
        self.assertEqual(
            self.c.sort_key("\u0430\u0306\u0334"),
            (0x1991, 0x0000, 0x0020, 0x004A, 0x0000, 0x0002, 0x0002, 0x0000)
        )

    def test_3(self):
        self.assertEqual(
            self.c.sort_key("\u0FB2\u0F71\u0001\u0F80\u0061"),
            (0x2571, 0x2587, 0x258A, 0x15EB, 0x0000, 0x0020, 0x0020, 0x0020,
                0x0020, 0x0000, 0x0002, 0x0002, 0x0002, 0x0002, 0x0000)
        )

    def test_4(self):
        self.assertEqual(
            self.c.sort_key("\u4E00\u0021"),
            (0xFB40, 0xCE00, 0x025D, 0x0000, 0x0020,
                0x0020, 0x0000, 0x0002, 0x0002, 0x0000)
        )

    def test_5(self):
        self.assertEqual(
            self.c.sort_key("\u3400\u0021"),
            (0xFB80, 0xB400, 0x025D, 0x0000, 0x0020,
                0x0020, 0x0000, 0x0002, 0x0002, 0x0000)
        )


if __name__ == "__main__":
    main()
