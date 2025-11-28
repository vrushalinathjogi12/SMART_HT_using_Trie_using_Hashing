import math

class BM25Search:
    """
    BM25 Search Engine Component
    used for ranked retrieval inside SMART-HT.
    """

    def __init__(self, inverted_index, doc_lengths, k1=1.5, b=0.75):
        self.inverted_index = inverted_index
        self.doc_lengths = doc_lengths

        self.k1 = k1
        self.b = b

        self.N = len(doc_lengths)  # total docs
        self.avgdl = sum(doc_lengths.values()) / max(1, self.N)

    def idf(self, term):
        """
        Inverse Document Frequency for a term.
        """
        df = len(self.inverted_index.get(term, {}))
        if df == 0:
            return 0

        return math.log((self.N - df + 0.5) / (df + 0.5) + 1)

    def score(self, query_terms):
        """
        Computes BM25 score for all documents.
        Returns sorted: highest score → lowest
        """
        scores = {}

        for term in query_terms:
            if term not in self.inverted_index:
                continue

            idf_val = self.idf(term)
            postings = self.inverted_index[term]

            for doc_id, freq in postings.items():
                dl = self.doc_lengths.get(doc_id, 0)

                score = (
                    idf_val
                    * (freq * (self.k1 + 1))
                    / (freq + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
                )

                scores[doc_id] = scores.get(doc_id, 0) + score

        return sorted(scores.items(), key=lambda x: x[1], reverse=True)
