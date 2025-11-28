from collections import defaultdict
import math

class RankingEngine:
    def __init__(self, inverted_index):
        self.index = inverted_index

    def score_documents(self, query_terms):
        """
        Returns list of (doc_id, base_score)
        """
        scores = defaultdict(float)
        for term in query_terms:
            docs = self.index.get_docs(term)
            idf = self.index.idf(term)
            for doc_id, tf in docs.items():
                doc_len = max(1, self.index.doc_lengths.get(doc_id, 1))
                tf_weight = tf / doc_len
                scores[doc_id] += tf_weight * idf
        # convert to list and sort
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked
