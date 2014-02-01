from __future__ import print_function

import sys

from pyuca import Collator
from pyuca.utils import display_sort_key

try:
    unichr
except NameError:
    unichr = chr


c = Collator()

prev_sort_key = None

success = 0
failure = 0

with open("CollationTest/CollationTest_NON_IGNORABLE.txt") as f:
    for line in f.readlines():
        points = line.split("#")[0].split(";")[0].strip().split()
        if points:
            try:
                test_string = "".join(
                    unichr(int(point, 16)) for point in points
                )
            except ValueError:  # Python 2 narrow builds will get this
                continue  # so just skip

            test_string_sort_key = c.sort_key(test_string)
            x = display_sort_key(test_string_sort_key)
            if prev_sort_key:
                if prev_sort_key > test_string_sort_key:
                    failure += 1
                else:
                    success += 1
            prev_sort_key = test_string_sort_key

print()
print("{} success; {} failure".format(success, failure))

if failure > 0:
    sys.exit(1)
