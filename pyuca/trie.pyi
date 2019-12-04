from typing import List, Optional, Tuple, Dict

class Node:
    value: Optional[List[List[int]]]
    children: Optional[Dict[int, Node]]
    def __init__(self) -> None: ...

class Trie:
    root: Node
    def __init__(self) -> None: ...
    def add(self, key: List[int], value: List[List[int]]) -> None: ...
    def find_prefix(
        self,
        key: List[int]
    ) -> Tuple[List[int], Optional[List[List[int]]], List[int]]: ...
