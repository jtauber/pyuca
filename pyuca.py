# pyuca - Unicode Collation Algorithm
#
# James Tauber
# http://jtauber.com/

# Copyright (c) 2006-2013 James Tauber and contributors
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


"""
Preliminary implementation of the Unicode Collation Algorithm.

This only implements the simple parts of the algorithm but I have successfully
tested it using the Default Unicode Collation Element Table (DUCET) to collate
Ancient Greek correctly.

Usage example:

    from pyuca import Collator
    c = Collator()

    sorted_words = sorted(words, key=c.sort_key)

Collator can also take an optional filename for specifying a custom collation
element table.
"""

import os.path


class Node:
    __slots__ = ("value", "children")
    
    def __init__(self):
        self.value = None
        self.children = None


class Trie:
    
    def __init__(self):
        self.root = Node()
    
    def add(self, key, value):
        curr_node = self.root
        for part in key:
            if curr_node.children is None:
                curr_node.children = {}
            curr_node = curr_node.children.setdefault(part, Node())
        curr_node.value = value
    
    def find_prefix(self, key):
        curr_node = self.root
        remainder = key
        for part in key:
            if curr_node.children is None or part not in curr_node.children:
                break
            curr_node = curr_node.children[part]
            remainder = remainder[1:]
        return (curr_node.value, remainder)


class Collator:

    def __init__(self, filename=None):
        
        if filename is None:
            filename = os.path.join(os.path.dirname(__file__), "allkeys.txt")
        self.table = Trie()
        self.load(filename)

    def load(self, filename):
        with open(filename) as keys_file:
            for line in keys_file:
                if line.startswith("#") or line.startswith("%"):
                    continue
                if line.strip() == "":
                    continue
                line = line[:line.find("#")] + "\n"
                line = line[:line.find("%")] + "\n"
                line = line.strip()
                
                if line.startswith("@"):
                    pass
                else:
                    semicolon = line.find(";")
                    char_list = line[:semicolon].strip().split()
                    x = line[semicolon:]
                    coll_elements = []
                    while True:
                        begin = x.find("[")
                        if begin == -1:
                            break
                        end = x[begin:].find("]")
                        coll_element = x[begin:begin + end + 1]
                        x = x[begin + 1:]
                        
                        chars = coll_element[2:-1].split(".")
                        
                        coll_elements.append(tuple(int(x, 16) for x in chars))
                    integer_points = [int(ch, 16) for ch in char_list]
                    self.table.add(integer_points, coll_elements)
    
    def sort_key(self, string):
        
        collation_elements = []
        
        lookup_key = [ord(ch) for ch in string]
        while lookup_key:
            value, lookup_key = self.table.find_prefix(lookup_key)
            if not value:
                # Calculate implicit weighting for CJK Ideographs
                # http://www.unicode.org/reports/tr10/#Implicit_Weights
                key = lookup_key[0]
                value = [
                    (0xFB40 + (key >> 15), 0x0020, 0x0002, 0x0001),
                    ((key & 0x7FFF) | 0x8000, 0x0000, 0x0000, 0x0000)
                ]
                lookup_key = lookup_key[1:]
            collation_elements.extend(value)
        sort_key = []
        
        for level in range(4):
            if level:
                sort_key.append(0)  # level separator
            for element in collation_elements:
                ce_l = element[level]
                if ce_l:
                    sort_key.append(ce_l)
        
        return tuple(sort_key)
