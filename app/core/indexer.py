# Lightweight Indexer: reads documents from a folder and populates engine components.
import os
from app.core.trie import Trie
from app.core.hash_store import HashStore
from app.core.inverted_index import InvertedIndex
from app.core.adaptive_ranker import AdaptiveRanker
from app.core.ranking import RankingEngine
from app.utils.tokenizer import tokenize

DOCS_DIR = "documents"

class Indexer:
    def __init__(self):
        self.trie = Trie()
        self.hash_store = HashStore()
        self.index = InvertedIndex()
        self.adaptive = AdaptiveRanker()
        self.ranker = RankingEngine(self.index)

    def rebuild_index(self, dirpath: str = DOCS_DIR, pattern: str = "*.txt", save: bool = False):
        import glob
        count = 0
        if not os.path.exists(dirpath):
            return 0
        for path in glob.glob(os.path.join(dirpath, pattern)):
            doc_id = os.path.basename(path)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            self.hash_store.add(doc_id, text)
            self.index.add_document(doc_id, text)
            for t in set(tokenize(text)):
                self.trie.insert(t, doc_id)
            count += 1
        return count
