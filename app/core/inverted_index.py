# app/core/inverted_index.py
from collections import defaultdict
import math

class InvertedIndex:
    """Inverted index: term -> {doc_id: frequency}"""

    def __init__(self):
        self.index = defaultdict(lambda: defaultdict(int))
        self.doc_count = 0
        self.doc_lengths = defaultdict(int)

    def add_document(self, doc_id, text):
        tokens = text.lower().split()
        for token in tokens:
            self.index[token][doc_id] += 1
        self.doc_lengths[doc_id] = len(tokens)
        self.doc_count += 1

    def remove_document(self, doc_id):
        for token in list(self.index.keys()):
            if doc_id in self.index[token]:
                del self.index[token][doc_id]
            if not self.index[token]:
                del self.index[token]
        if doc_id in self.doc_lengths:
            del self.doc_lengths[doc_id]
            self.doc_count -= 1

    def get_postings(self, term):
        return self.index.get(term, {})

    def tf_idf(self, term, doc_id):
        tf = self.index.get(term, {}).get(doc_id, 0)
        if tf == 0:
            return 0
        df = len(self.index.get(term, {}))
        idf = math.log((self.doc_count + 1) / (df + 1)) + 1
        return tf * idf
