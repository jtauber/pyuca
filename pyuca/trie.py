"""A minimal prefix trie used to match DUCET contractions greedily."""

from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class Node(Generic[K, V]):
    __slots__ = ("value", "children")

    def __init__(self) -> None:
        self.value: V | None = None
        self.children: dict[K, Node[K, V]] | None = None


class Trie(Generic[K, V]):
    def __init__(self) -> None:
        self.root: Node[K, V] = Node()

    def add(self, key: list[K], value: V) -> None:
        curr_node = self.root
        for part in key:
            if curr_node.children is None:
                curr_node.children = {}
            curr_node = curr_node.children.setdefault(part, Node())
        curr_node.value = value

    def find_prefix_from(self, key: list[K], start: int = 0) -> tuple[int, V | None]:
        """Longest value-bearing prefix of ``key`` starting at ``start``.

        Returns ``(end, value)`` where ``end`` is the index just past the match
        (``start`` if nothing matched) and ``value`` is that entry's value (or
        ``None``). Index-based to avoid allocating slices on the hot path.
        """
        curr_node = self.root
        success_index = start
        success_value: V | None = None
        for i in range(start, len(key)):
            children = curr_node.children
            if children is None:
                break
            next_node = children.get(key[i])
            if next_node is None:
                break
            curr_node = next_node
            if curr_node.value is not None:
                success_index = i + 1
                success_value = curr_node.value
        return success_index, success_value

    def find_prefix(self, key: list[K]) -> tuple[list[K], V | None, list[K]]:
        end, value = self.find_prefix_from(key)
        return key[:end], value, key[end:]
