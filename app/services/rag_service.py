from ..generation.citation_validator import validate_citations
from ..generation.generator import AnswerGenerator
from ..retrieval.semantic_retriever import SemanticRetriever


class RAGService:
    def __init__(self, retriever: SemanticRetriever, generator: AnswerGenerator):
        self.retriever = retriever
        self.generator = generator

    def ask(self, question: str, top_k: int = 4, filename: str | None = None) -> dict:
        evidence = self.retriever.search(question, top_k=top_k, filename=filename)
        result = self.generator.generate(question, evidence)
        result["evidence"] = evidence
        result["citations"] = validate_citations(result["answer"], evidence)
        return result
