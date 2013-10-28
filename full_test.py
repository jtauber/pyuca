#!/usr/bin/env python3

from pyuca import Collator

c = Collator()

prev = None

with open("CollationTest/CollationTest_NON_IGNORABLE_SHORT.txt") as f:
    for line in f.readlines():
        l = line.split("#")[0].strip()
        if l:
            test_string = "".join(chr(int(s, 16)) for s in line.strip().split())
            a, b = sorted([prev, test_string], key=c.sort_key)
            if a == prev:
                print(True)
            else:
                print(False)
            prev = test_string
