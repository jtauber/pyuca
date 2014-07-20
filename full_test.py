from __future__ import unicode_literals

import sys
from io import open

from pyuca import Collator
from pyuca.collator import UCA_VERSION
from pyuca.utils import format_sort_key

try:
    chr = unichr
except NameError:
    pass

c = Collator()

prev_sort_key = None

success = 0
failure = 0

path = "CollationTest/{0}/CollationTest_NON_IGNORABLE.txt".format(UCA_VERSION)

with open(path) as f:
    for i, line in enumerate(f.readlines()):
        points = line.split("#", 1)[0].split(";", 1)[0].strip().split()

        if points:
            test_string = "".join(
                chr(int(point, 16)) for point in points
            )
            test_string_sort_key = c.sort_key(test_string)
            x = format_sort_key(test_string_sort_key)
            if prev_sort_key:
                if prev_sort_key > test_string_sort_key:
                    failure += 1
                    print(i)
                    print(line)
                    print(x)
                    print('-------')
                else:
                    success += 1
            prev_sort_key = test_string_sort_key

print()
print("{0} success; {1} failure (UCA version {2})".format(
    success, failure, UCA_VERSION))

if failure > 0:
    sys.exit(1)
