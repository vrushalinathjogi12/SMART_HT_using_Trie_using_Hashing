"""
Persistence helpers: saves index components to disk in JSON/pickle-friendly ways.
We avoid pickling locks by saving simple data structures.
"""

import os, json, gzip, pickle
from app.core.trie import Trie
from app.core.inverted_index import InvertedIndex
from app.core.hash_store import HashStore
from app.core.adaptive_ranker import AdaptiveRanker
from app.core.smart_ht_engine import SmartHTEngine

INDEX_DIR = os.path.join("data", "index")
ENGINE_PATH = os.path.join(INDEX_DIR, "smart_ht_engine.pkl.gz")
TRIE_PATH = os.path.join(INDEX_DIR, "trie_words.json")
HASH_PATH = os.path.join(INDEX_DIR, "hash_store.json")
INVERTED_PATH = os.path.join(INDEX_DIR, "inverted_index.json")
CLICK_LOG_PATH = os.path.join(INDEX_DIR, "click_logs.json")

os.makedirs(INDEX_DIR, exist_ok=True)

def save_engine(engine: SmartHTEngine):
    """
    Save inverted index and hash store and trie words (simple representation).
    AdaptiveRanker already saves click logs.
    """
    # save inverted index as JSON: term -> {doc_id: freq}
    inv = {}
    for term, docs in engine.index.index.items():
        inv[term] = docs
    with open(INVERTED_PATH, "w", encoding="utf-8") as f:
        json.dump(inv, f)

    # save hash_store
    hs = getattr(engine.hash_store, "store", {})
    with open(HASH_PATH, "w", encoding="utf-8") as f:
        json.dump(hs, f)

    # save trie as list of words via a simple traversal
    words = []
    def dfs(node, path):
        if getattr(node, "is_end", False):
            words.append("".join(path))
        for c, child in getattr(node, "children", {}).items():
            dfs(child, path + [c])
    dfs(engine.trie.root, [])
    with open(TRIE_PATH, "w", encoding="utf-8") as f:
        json.dump(words, f)

    # try to save engine metadata (optional pickle)
    try:
        with gzip.open(ENGINE_PATH, "wb") as f:
            # Only save a minimal serializable snapshot
            snapshot = {
                "doc_count": len(hs),
            }
            pickle.dump(snapshot, f)
    except Exception:
        pass

def load_engine():
    """
    Reconstruct a SmartHTEngine from persisted files if they exist.
    Returns SmartHTEngine or None.
    """
    try:
        if not (os.path.exists(INVERTED_PATH) and os.path.exists(HASH_PATH) and os.path.exists(TRIE_PATH)):
            return None
        engine = SmartHTEngine()
        # load inverted
        with open(INVERTED_PATH, "r", encoding="utf-8") as f:
            inv = json.load(f)
        engine.index = InvertedIndex()
        for term, docs in inv.items():
            engine.index.index[term] = {k:int(v) for k,v in docs.items()}
        # load hash
        with open(HASH_PATH, "r", encoding="utf-8") as f:
            hs = json.load(f)
        engine.hash_store = HashStore()
        engine.hash_store.store = {k:v for k,v in hs.items()}
        # load trie words
        with open(TRIE_PATH, "r", encoding="utf-8") as f:
            words = json.load(f)
        engine.trie = Trie()
        for w in words:
            engine.trie.insert(w)
        # adaptive ranker already loads its click logs on init
        engine.adaptive = AdaptiveRanker()
        engine.ranker = engine.ranker.__class__(engine.index)
        return engine
    except Exception:
        return None
