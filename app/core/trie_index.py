class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False


class TrieIndex:
    """
    Trie-based Keyword Index.
    Supports:
    - fast prefix search
    - autocomplete
    """

    def __init__(self):
        self.root = TrieNode()

    # ------------------------------------
    # Insert keyword into Trie
    # ------------------------------------
    def insert(self, word: str):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    # ------------------------------------
    # Autocomplete: return words starting with prefix
    # ------------------------------------
    def autocomplete(self, prefix: str, limit: int = 10):
        node = self.root

        # Traverse to end of prefix
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        # DFS to collect words
        results = []
        self._dfs(node, prefix, results, limit)
        return results

    def _dfs(self, node, prefix, results, limit):
        if len(results) >= limit:
            return

        if node.is_end:
            results.append(prefix)

        for char, child in node.children.items():
            self._dfs(child, prefix + char, results, limit)
