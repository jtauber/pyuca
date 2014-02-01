
def hexstrings2int(hexstrings):
    return [int(hexstring, 16) for hexstring in hexstrings]


def int2hexstrings(number_list):
    return ["{:04X}".format(n) for n in number_list]


def display_collation_elements(collation_elements):
    if collation_elements is None:
        return None
    else:
        return ", ".join(
            "[" + ".".join(
                int2hexstrings(collation_element)
            ) + "]" for collation_element in collation_elements
        )


def display_sort_key(sort_key):
    return " ".join(
        ("{:04X}".format(x) if x else "|") for x in sort_key
    )
