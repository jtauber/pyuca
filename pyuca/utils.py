
def hexstrings2int(hexstrings):
    return tuple(int(hexstring, 16) for hexstring in hexstrings)


def display_collation_element_array(collation_element_array):
    return ", ".join(
        "[" + ".".join(
            "{:04X}".format(n)
            for n in collation_element
        ) + "]" for collation_element in collation_element_array
    )


def display_sort_key(sort_key):
    return " ".join(
        "{:04X}".format(x) for x in sort_key
    )