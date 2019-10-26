from __future__ import unicode_literals

import sys
from io import open

from pyuca import Collator

from pyuca.collator import (
    Collator_5_2_0, Collator_6_3_0,
    Collator_8_0_0, Collator_9_0_0, Collator_10_0_0
)
from pyuca.utils import format_sort_key

try:
    chr = unichr
except NameError:
    pass

PYTHON3 = sys.version_info >= (3,)
V8_0_0 = sys.version_info >= (3, 5)
V9_0_0 = sys.version_info >= (3, 6)
V10_0_0 = sys.version_info >= (3, 7)

collators = [Collator_5_2_0]
if PYTHON3:
    collators.append(Collator_6_3_0)
if V8_0_0:
    collators.append(Collator_8_0_0)
if V9_0_0:
    collators.append(Collator_9_0_0)
if V10_0_0:
    collators.append(Collator_10_0_0)

default_collator = Collator

collators = [
    collator for collator in collators
    if collator.UCA_VERSION != default_collator.UCA_VERSION
] + [default_collator]


total_failures = 0

for coll in collators:

    c = coll(alternate="shifted")

    prev_sort_key = None

    success = 0
    failure = 0

    path = "CollationTest/{0}/CollationTest_SHIFTED.txt".format(
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
