# app/core/index_manager.py
from app.core.trie import Trie
from app.core.hash_store import HashStore
from app.core.inverted_index import InvertedIndex
from app.core.adaptive_ranker import AdaptiveRanker
import re

def tokenize(text):
    return re.findall(r'\w+', text.lower())

class IndexManager:
    """Manages HashStore + Trie + InvertedIndex"""

    def __init__(self, data_path="data/documents"):
        self.data_path = data_path
        self.hash_store = HashStore()
        self.trie = Trie()
        self.index = InvertedIndex()
        self.adaptive = AdaptiveRanker()
        self.build_index()

    def build_index(self):
        """Build index from all documents in folder"""
        import os
        for filename in os.listdir(self.data_path):
            file_path = os.path.join(self.data_path, filename)
            if os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                self.hash_store.set(filename, text)
                self.index.add_document(filename, text)
                for token in set(tokenize(text)):
                    self.trie.insert(token, filename)

    def search(self, query):
        tokens = tokenize(query)
        results = {}
        for token in tokens:
            postings = self.index.get_postings(token)
            for doc_id, _ in postings.items():
                results[doc_id] = sum(self.index.tf_idf(t, doc_id) for t in tokens)
        ranked = sorted(results.items(), key=lambda x: x[1], reverse=True)
        return ranked  # [(doc_id, base_score), ...]

    def autocomplete(self, prefix, limit=10):
        doc_ids = self.trie.prefix_search(prefix)
        return doc_ids[:limit]

    def get_snippet(self, doc_id, query, max_len=160):
        text = self.hash_store.get(doc_id)
        text_l = text.lower()
        for token in tokenize(query):
            idx = text_l.find(token)
            if idx != -1:
                start = max(0, idx - 40)
                end = min(len(text), idx + 40)
                snippet = text[start:end].replace("\n", " ").strip()
                if len(snippet) < len(text):
                    snippet += "..."
                return snippet
        return (text[:max_len] + "...") if len(text) > max_len else text
