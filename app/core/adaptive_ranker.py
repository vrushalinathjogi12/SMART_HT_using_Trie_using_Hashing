import json, os, time
from collections import defaultdict

DEFAULT_LOG_PATH = os.path.join("data", "index", "click_logs.json")

class AdaptiveRanker:
    def __init__(self, log_path: str = DEFAULT_LOG_PATH, alpha: float = 0.6, decay_rate: float = 30*24*3600, min_clicks: int = 1):
        self.log_path = log_path
        self.alpha = float(alpha)
        self.decay_rate = float(decay_rate)
        self.min_clicks = int(min_clicks)
        self.query_clicks = defaultdict(lambda: defaultdict(list))
        self.global_clicks = defaultdict(list)
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        self._load()

    def _load(self):
        if not os.path.exists(self.log_path): return
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            for q, dmap in raw.get("query_clicks", {}).items():
                for d, ts_list in dmap.items():
                    self.query_clicks[q][d] = [float(t) for t in ts_list]
            for d, ts_list in raw.get("global_clicks", {}).items():
                self.global_clicks[d] = [float(t) for t in ts_list]
        except Exception:
            self.query_clicks = defaultdict(lambda: defaultdict(list))
            self.global_clicks = defaultdict(list)

    def _save(self):
        out = {
            "query_clicks": {q: {d: ts_list for d, ts_list in dmap.items()} for q, dmap in self.query_clicks.items()},
            "global_clicks": {d: ts_list for d, ts_list in self.global_clicks.items()}
        }
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(out, f)

    def record_click(self, query: str, doc_id: str, timestamp: float = None):
        try:
            ts = float(timestamp if timestamp is not None else time.time())
        except (ValueError, TypeError):
            ts = time.time()
        if not isinstance(query, str) or not isinstance(doc_id, str):
            return
        q = query.strip().lower()
        self.query_clicks[q][doc_id].append(ts)
        self.global_clicks[doc_id].append(ts)
        self._save()

    def _decay_weight(self, ts: float, now: float):
        age = max(0.0, now - ts)
        return float((2.718281828459045) ** (-age / self.decay_rate))

    def query_doc_boost(self, query: str, doc_id: str):
        q = query.strip().lower()
        now = time.time()
        click_times = self.query_clicks.get(q, {}).get(doc_id, [])
        if not click_times:
            return 0.0
        weight = sum(self._decay_weight(ts, now) for ts in click_times)
        if weight < self.min_clicks * 0.1:
            return 0.0
        boost = self.alpha * (1.0 - (2.718281828459045 ** (-weight)))
        return float(boost)

    def global_doc_boost(self, doc_id: str):
        now = time.time()
        times = self.global_clicks.get(doc_id, [])
        if not times:
            return 0.0
        weight = sum(self._decay_weight(ts, now) for ts in times)
        pop_boost = (self.alpha / 4.0) * (1.0 - (2.718281828459045 ** (-weight / 2.0)))
        return float(pop_boost)

    def apply_boosts(self, ranked_docs, query: str):
        out = []
        for doc_id, base in ranked_docs:
            qboost = self.query_doc_boost(query, doc_id)
            gboost = self.global_doc_boost(doc_id)
            total_boost = qboost + gboost
            boosted_score = float(base * (1.0 + total_boost))
            out.append((doc_id, boosted_score, float(base), float(total_boost)))
        return sorted(out, key=lambda x: x[1], reverse=True)

    def reset_logs(self):
        self.query_clicks = defaultdict(lambda: defaultdict(list))
        self.global_clicks = defaultdict(list)
        self._save()
