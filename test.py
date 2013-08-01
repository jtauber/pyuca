# encoding: utf-8

# to work on both Python2 and Python3, I use u"..." but that means Python3
# must be 3.3 or later.

# this also assumes you've downloaded allkeys.txt from
# http://www.unicode.org/Public/UCA/latest/allkeys.txt

from unittest import TestCase


class SmokeTest(TestCase):
    
    def test_cafe(self):
        from pyuca import Collator
        c = Collator("allkeys.txt")
        
        self.assertEqual(sorted(["cafe", "caff", u"café"]), ["cafe", "caff", u"café"])
        self.assertEqual(sorted(["cafe", "caff", u"café"], key=c.sort_key), ["cafe", u"café", "caff"])
