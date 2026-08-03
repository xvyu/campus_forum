"""DFA + Trie 树敏感词过滤"""
from app.errors import SensitiveWordError

_trie: dict = {}
_built = False


def build_trie(words: list[str]) -> None:
    """构建敏感词 Trie 树"""
    global _trie, _built
    _trie = {}
    for word in words:
        node = _trie
        for char in word:
            node = node.setdefault(char, {})
        node["#"] = True
    _built = True


def check(text: str) -> bool:
    """检查文本是否包含敏感词，True=包含"""
    if not _built:
        return False
    length = len(text)
    for i in range(length):
        node = _trie
        for j in range(i, length):
            char = text[j]
            if char not in node:
                break
            node = node[char]
            if "#" in node:
                return True
    return False


def check_or_raise(text: str) -> None:
    """检查敏感词，含则抛 SensitiveWordError"""
    if check(text):
        raise SensitiveWordError()
