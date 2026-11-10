class SemanticRetriever:
    def __init__(self, embedding_model, vector_store):
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    def search(self, query: str, top_k: int = 5, filename: str | None = None):
        if not query or not query.strip():
            raise ValueError("Enter a search query.")
        if not self.vector_store.metadata:
            return []
        vector = self.embedding_model.encode(query.strip(), normalize=True)[0]
        candidates = self.vector_store.search(vector, top_k=max(top_k * 4, top_k))
        if filename and filename != "All documents":
            candidates = [item for item in candidates if item.get("filename") == filename]
        return candidates[:top_k]

    def index(self, chunks, replace: bool = True):
        if not chunks:
            if replace:
                self.vector_store.save([], [])
            return
        texts = [chunk["text"] for chunk in chunks]
        vectors = self.embedding_model.encode(texts, normalize=True)
        if replace:
            self.vector_store.save(vectors, chunks)
        else:
            old_vectors = self.vector_store.vectors
            combined_vectors = vectors if old_vectors.size == 0 else __import__("numpy").vstack((old_vectors, vectors))
            self.vector_store.save(combined_vectors, self.vector_store.metadata + chunks)
