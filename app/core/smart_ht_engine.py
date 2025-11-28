from app.utils.tokenizer import tokenize
from app.core.trie import Trie
from app.core.hash_store import HashStore
from app.core.inverted_index import InvertedIndex
from app.core.ranking import RankingEngine
from app.core.adaptive_ranker import AdaptiveRanker

class SmartHTEngine:
    def __init__(self, adaptive_ranker: AdaptiveRanker = None):
        self.trie = Trie()
        self.hash_store = HashStore()
        self.index = InvertedIndex()
        self.ranker = RankingEngine(self.index)
        self.adaptive = adaptive_ranker if adaptive_ranker else AdaptiveRanker()

    def autocomplete(self, prefix: str, limit: int = 10):
        if not prefix:
            return []
        return self.trie.prefix_search(prefix)[:limit]

    def index_document(self, doc_id: str, text: str):
        self.hash_store.add(doc_id, text)
        self.index.add_document(doc_id, text)
        for t in set(tokenize(text)):
            self.trie.insert(t, doc_id)

    def remove_document(self, doc_id: str):
        self.index.remove_document(doc_id)
        self.hash_store.remove(doc_id)

    def _expand_query_terms(self, q_tokens):
        expanded = []
        seen = set()
        for t in q_tokens:
            if self.trie.exists(t) and t not in seen:
                expanded.append(t); seen.add(t)
            for e in self.trie.prefix_search(t):
                if e not in seen:
                    expanded.append(e); seen.add(e)
        return expanded

    def _snippet(self, text: str, query_tokens, max_len=180):
        text_l = text.lower()
        for t in query_tokens:
            idx = text_l.find(t)
            if idx != -1:
                start = max(0, idx-50)
                end = min(len(text), idx+50)
                s = text[start:end].replace("\n"," ").strip()
                return s + "..." if len(s) < len(text) else s
        return (text[:max_len] + "...") if len(text) > max_len else text

    def search(self, query: str, top_k: int = 10):
        if not query or not query.strip():
            return []
        q_tokens = tokenize(query)
        expanded_terms = self._expand_query_terms(q_tokens)
        for t in q_tokens:
            if t not in expanded_terms:
                expanded_terms.append(t)
        ranked = self.ranker.score_documents(expanded_terms)  # returns list of (doc_id, score)
        # RankingEngine returns list of tuples (doc_id, score) - AdaptiveRanker expects that same format
        boosted = self.adaptive.apply_boosts(ranked, query)
        results = []
        for doc_id, boosted_score, base_score, total_boost in boosted[:top_k]:
            text = self.hash_store.get(doc_id) or ""
            results.append({
                "doc_id": doc_id,
                "base_score": round(base_score, 6),
                "boosted_score": round(boosted_score, 6),
                "total_boost": round(total_boost, 6),
                "snippet": self._snippet(text, q_tokens)
            })
        return results

    def record_click(self, query: str, doc_id: str, timestamp: float = None):
        self.adaptive.record_click(query, doc_id, timestamp)

    def get_document(self, doc_id: str):
        return self.hash_store.get(doc_id)
