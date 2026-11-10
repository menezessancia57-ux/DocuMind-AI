import numpy as np

from app.retrieval.vector_store import VectorStore
from app.retrieval.semantic_retriever import SemanticRetriever


class FixedEmbeddingModel:
    def encode(self, texts, normalize=True):
        if isinstance(texts, str):
            texts = [texts]
        vectors = []
        for text in texts:
            text = text.lower()
            vectors.append([1.0 if "document" in text else 0.0, 1.0 if "search" in text else 0.0])
        return np.asarray(vectors, dtype=np.float32)


def test_vector_store_ranking_and_filter(tmp_path):
    store = VectorStore(tmp_path / "index.npy", tmp_path / "metadata.json")
    vectors = np.asarray([[1, 0], [0, 1]], dtype=np.float32)
    metadata = [
        {"text": "document one", "filename": "a.pdf", "page_number": 1, "chunk_id": "a"},
        {"text": "search two", "filename": "b.pdf", "page_number": 2, "chunk_id": "b"},
    ]
    store.save(vectors, metadata)
    results = store.search([1, 0], 2)
    assert results[0]["filename"] == "a.pdf"


def test_retriever_empty_query():
    retriever = SemanticRetriever(FixedEmbeddingModel(), VectorStore())
    try:
        retriever.search("", 5)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_retriever_index_and_filter(tmp_path):
    store = VectorStore(tmp_path / "index.npy", tmp_path / "metadata.json")
    retriever = SemanticRetriever(FixedEmbeddingModel(), store)
    retriever.index([{"text": "document search", "filename": "a.pdf", "page_number": 1, "chunk_id": "1"}])
    assert retriever.search("document", 5, "a.pdf")[0]["filename"] == "a.pdf"
