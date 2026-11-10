import hashlib
import logging
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self.load_error = None
        self.backend = "not loaded"

    def _ensure_loaded(self):
        if self._model is not None or self.load_error is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            self.backend = "sentence-transformers"
        except Exception as exc:
            self.load_error = exc
            self.backend = "offline-hash"
            logger.exception("Sentence Transformer could not be initialized; using offline hash embeddings")

    def encode(self, texts, normalize: bool = True) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]
        texts = list(texts)
        if not texts:
            return np.empty((0, 384), dtype=np.float32)
        self._ensure_loaded()
        if self._model is not None:
            vectors = np.asarray(self._model.encode(texts, show_progress_bar=False), dtype=np.float32)
        else:
            vectors = np.vstack([self._hash_embedding(text) for text in texts]).astype(np.float32)
        if normalize:
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            vectors = np.divide(vectors, norms, out=np.zeros_like(vectors), where=norms != 0)
        return vectors

    def _hash_embedding(self, text: str, dimensions: int = 384) -> np.ndarray:
        vector = np.zeros(dimensions, dtype=np.float32)
        for token in str(text).lower().split():
            digest = hashlib.blake2b(token.encode("utf-8", errors="ignore"), digest_size=8).digest()
            number = int.from_bytes(digest, "little")
            vector[number % dimensions] += 1.0
        return vector
