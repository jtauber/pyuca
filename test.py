# encoding: utf-8

# to work on both Python2 and Python3, I use u"..." but that means Python3
# must be 3.3 or later.

from unittest import TestCase


class SmokeTest(TestCase):

    def test_cafe(self):
        from pyuca import Collator
        c = Collator()

        self.assertEqual(sorted(["cafe", "caff", u"café"]), ["cafe", "caff", u"café"])
        self.assertEqual(sorted(["cafe", "caff", u"café"], key=c.sort_key), ["cafe", u"café", "caff"])
