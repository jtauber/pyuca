# encoding: utf-8

# to work on both Python2 and Python3, I use u"..." but that means Python3
# must be 3.3 or later.

from unittest import TestCase, main


class SmokeTest(TestCase):

    def test_cafe(self):
        from pyuca import Collator
        c = Collator()

        self.assertEqual(sorted(["cafe", "caff", u"café"]), ["cafe", "caff", u"café"])
        self.assertEqual(sorted(["cafe", "caff", u"café"], key=c.sort_key), ["cafe", u"café", "caff"])


class TrieTest(TestCase):

    def test_trie(self):
        from pyuca.trie import Trie

        t = Trie()
        t.add("foo", "bar")
        self.assertEqual(t.find_prefix("fo"), ("fo", None, ""))
        self.assertEqual(t.find_prefix("foo"), ("foo", "bar", ""))
        self.assertEqual(t.find_prefix("food"), ("foo", "bar", "d"))


if __name__ == "__main__":
    main()
