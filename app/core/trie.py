# app/core/trie.py
from collections import defaultdict

class TrieNode:
    def __init__(self):
        self.children = defaultdict(TrieNode)
        self.docs = set()
        self.is_end = False

class Trie:
    """Trie for prefix search + keyword indexing"""

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, doc_id=None):
        node = self.root
        for char in word.lower():
            node = node.children[char]
        node.is_end = True
        if doc_id:
            node.docs.add(doc_id)

    def exists(self, word):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end

    def prefix_search(self, prefix):
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        results = set()
        self._dfs(node, results)
        return list(results)

    def _dfs(self, node, results):
        results.update(node.docs)
        for child in node.children.values():
            self._dfs(child, results)
