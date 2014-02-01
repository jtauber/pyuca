#!/usr/bin/env python3

from pyuca import Collator
from pyuca.utils import display_sort_key


c = Collator()

prev = None

with open("CollationTest/CollationTest_NON_IGNORABLE_SHORT.txt") as f:
    for line in f.readlines():
        print(line.strip(), end=": ")
        points = line.split("#")[0].strip().split()
        if points:
            test_string = "".join(chr(int(point, 16)) for point in points)
            print(display_sort_key(c.sort_key(test_string)))
            if prev:
                if c.sort_key(prev) > c.sort_key(test_string):
                    break
            prev = test_string
