import re


class MockClient:
    def generate(self, question: str, evidence: list[dict]) -> dict:
        if not evidence:
            return {"answer": "The answer cannot be established from the uploaded documents.", "type": "extractive"}
        question_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", question.lower()))
        scored = []
        for item in evidence:
            overlap = len(question_words.intersection(set(re.findall(r"\b[a-zA-Z]{4,}\b", item["text"].lower()))))
            scored.append((overlap, item))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        best = scored[0][1]
        sentences = re.split(r"(?<=[.!?])\s+", best["text"])
        relevant = sentences[0] if sentences else best["text"][:500]
        citation = format_citation_local(best)
        answer = f"Based on the uploaded documents, {relevant} {citation}"
        return {"answer": answer, "type": "extractive"}


def format_citation_local(item: dict) -> str:
    return f"[{item.get('filename', 'unknown')}, page {item.get('page_number', '?')}]"
