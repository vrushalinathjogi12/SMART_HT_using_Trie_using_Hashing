# app/core/hash_store.py
import os
import json

class HashStore:
    """Simple key-value storage for documents."""

    def __init__(self, data_path="data/index/hash_store.json"):
        self.data_path = data_path
        self.store = {}
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        self._load()

    def _load(self):
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    self.store = json.load(f)
            except Exception:
                self.store = {}

    def _save(self):
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(self.store, f, ensure_ascii=False)

    def set(self, doc_id, text):
        self.store[doc_id] = text
        self._save()

    def get(self, doc_id):
        return self.store.get(doc_id, "")

    def remove(self, doc_id):
        if doc_id in self.store:
            del self.store[doc_id]
            self._save()
