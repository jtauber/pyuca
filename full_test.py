from __future__ import unicode_literals

import sys
from io import open

from pyuca.collator import (
    Collator_5_2_0, Collator_6_3_0,
    Collator_8_0_0, Collator_9_0_0, Collator_10_0_0
)
from pyuca.utils import format_sort_key

try:
    chr = unichr
except NameError:
    pass


total_failures = 0

for coll in [
    Collator_5_2_0, Collator_6_3_0,
    Collator_8_0_0, Collator_9_0_0, Collator_10_0_0
]:

    c = coll()

    prev_sort_key = None

    success = 0
    failure = 0

    path = "CollationTest/{0}/CollationTest_NON_IGNORABLE.txt".format(
        c.UCA_VERSION)

    with open(path) as f:
        for i, line in enumerate(f.readlines()):
            points = line.split("#", 1)[0].split(";", 1)[0].strip().split()

            if points:
                test_string = "".join(
                    chr(int(point, 16)) for point in points
                )
                test_string_sort_key = c.sort_key(test_string)
                if prev_sort_key:
                    if prev_sort_key > test_string_sort_key:
                        failure += 1
                        print("-------")
                        print("failed on line {0}:".format(i+1))
                        print(line.rstrip("\n"))
                        print("PREV: {0}".format(
                            format_sort_key(prev_sort_key)))
                        print("THIS: {0}".format(
                            format_sort_key(test_string_sort_key)))
                        print("-------")
                    else:
                        success += 1
                prev_sort_key = test_string_sort_key

    print("")
    print("{0} success; {1} failure (UCA version {2})".format(
        success, failure, c.UCA_VERSION))

    total_failures += failure

if total_failures > 0:
    sys.exit(1)
