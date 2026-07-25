from pyuca.trie import Trie


def test_prefix_matching():
    t: Trie[str, str] = Trie()
    t.add("foo", "bar")
    assert t.find_prefix("fo") == ("", None, "fo")
    assert t.find_prefix("foo") == ("foo", "bar", "")
    assert t.find_prefix("food") == ("foo", "bar", "d")


def test_longest_prefix_wins():
    t: Trie[str, str] = Trie()
    t.add("a", "yes")
    t.add("abc", "yes")
    assert t.find_prefix("abdc") == ("a", "yes", "bdc")
