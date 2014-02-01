
def hexstrings2int(hexstrings):
    return [int(hexstring, 16) for hexstring in hexstrings]


def display_collation_elements(collation_elements):
    return ", ".join(
        "[" + ".".join(
            "{:04X}".format(n)
            for n in collation_element
        ) + "]" for collation_element in collation_elements
    )


def display_sort_key(sort_key):
    return " ".join(
        ("{:04X}".format(x) if x else "|") for x in sort_key
    )
