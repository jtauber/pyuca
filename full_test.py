from __future__ import unicode_literals

import sys
from io import open

from pyuca import Collator
from pyuca.utils import format_sort_key

try:
    chr = unichr
except NameError:
    pass

c = Collator()

prev_sort_key = None

success = 0
failure = 0

with open("CollationTest/CollationTest_NON_IGNORABLE.txt") as f:
    for line in f.readlines():
        points = line.split("#")[0].split(";")[0].strip().split()
        if points:
            test_string = "".join(
                chr(int(point, 16)) for point in points
            )
            test_string_sort_key = c.sort_key(test_string)
            x = format_sort_key(test_string_sort_key)
            if prev_sort_key:
                if prev_sort_key > test_string_sort_key:
                    failure += 1
                    print(line)
                    print(x)
                else:
                    success += 1
            prev_sort_key = test_string_sort_key

print()
print("{} success; {} failure".format(success, failure))

if failure > 0:
    sys.exit(1)
