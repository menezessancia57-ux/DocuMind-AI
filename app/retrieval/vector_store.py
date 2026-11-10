import json
from pathlib import Path
import numpy as np


class VectorStore:
    def __init__(self, index_path=None, metadata_path=None):
        self.index_path = Path(index_path) if index_path else None
        self.metadata_path = Path(metadata_path) if metadata_path else None
        self.metadata = []
        self.vectors = np.empty((0, 0), dtype=np.float32)
        self._load()

    def _load(self):
        if self.metadata_path and self.metadata_path.exists():
            try:
                payload = json.loads(self.metadata_path.read_text(encoding="utf-8"))
                self.metadata = payload.get("metadata", [])
            except (json.JSONDecodeError, OSError):
                self.metadata = []
        if self.index_path and self.index_path.exists():
            try:
                self.vectors = np.load(self.index_path, allow_pickle=False)
            except (ValueError, OSError):
                self.vectors = np.empty((0, 0), dtype=np.float32)

    def save(self, vectors, metadata):
        self.vectors = np.asarray(vectors, dtype=np.float32)
        self.metadata = metadata
        if self.index_path:
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            np.save(self.index_path, self.vectors)
        if self.metadata_path:
            self.metadata_path.write_text(json.dumps({"metadata": metadata}, ensure_ascii=False), encoding="utf-8")

    def search(self, query_vector, top_k=5):
        if not self.metadata or self.vectors.size == 0:
            return []
        query = np.asarray(query_vector, dtype=np.float32).reshape(1, -1)
        if query.shape[1] != self.vectors.shape[1]:
            raise ValueError("Query and index dimensions do not match.")
        similarities = self.vectors @ query[0]
        count = min(max(top_k, 0), len(self.metadata))
        indices = np.argsort(-similarities)[:count]
        return [{**self.metadata[int(index)], "score": float(similarities[int(index)])} for index in indices]

    def remove_document(self, document_id: str = "", filename: str = "") -> int:
        keep_indices = [
            index for index, item in enumerate(self.metadata)
            if item.get("document_id") != document_id and item.get("filename") != filename
        ]
        removed = len(self.metadata) - len(keep_indices)
        if removed:
            keep = [self.metadata[index] for index in keep_indices]
            self.save(self.vectors[keep_indices], keep)
        return removed

    def clear(self):
        self.vectors = np.empty((0, 0), dtype=np.float32)
        self.metadata = []
        for path in (self.index_path, self.metadata_path):
            if path and path.exists():
                path.unlink()
