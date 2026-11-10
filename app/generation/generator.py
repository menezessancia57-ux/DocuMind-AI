import os
from .mock_client import MockClient
from .prompts import build_rag_prompt


class AnswerGenerator:
    def __init__(self, api_key: str | None = None, model: str = "gemini-2.0-flash"):
        supplied_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY")
        self.api_key = supplied_key.strip() if supplied_key else None
        self.model = model
        self.mock_client = MockClient()

    @property
    def mode(self) -> str:
        return "Gemini" if self.api_key else "Local extractive"

    def generate(self, question: str, evidence: list[dict]) -> dict:
        if not question or not question.strip():
            raise ValueError("Enter a question.")
        if not evidence:
            return {"answer": "The answer cannot be established from the uploaded documents.", "type": "insufficient_evidence", "citations": []}
        if not self.api_key:
            return self.mock_client.generate(question, evidence)
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(model=self.model, contents=build_rag_prompt(question, evidence))
            answer = getattr(response, "text", "") or ""
            if not answer.strip():
                raise RuntimeError("Gemini returned an empty response")
            return {"answer": answer, "type": "generated", "citations": []}
        except Exception as exc:
            result = self.mock_client.generate(question, evidence)
            result["warning"] = f"Gemini request failed; local extractive evidence was used instead ({type(exc).__name__})."
            return result
