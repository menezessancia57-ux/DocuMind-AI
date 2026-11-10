from app.generation.generator import AnswerGenerator
from app.generation.mock_client import MockClient


def test_demo_answer_and_citation():
    evidence = [{"text": "Renewable energy uses wind and solar resources.", "filename": "energy.pdf", "page_number": 2}]
    result = MockClient().generate("What is renewable energy?", evidence)
    assert result["type"] == "extractive"
    assert "[energy.pdf, page 2]" in result["answer"]


def test_missing_evidence():
    result = MockClient().generate("What does the collection say?", [])
    assert result["answer"] == "The answer cannot be established from the uploaded documents."


def test_generator_without_key_is_demo(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    generator = AnswerGenerator(api_key=None)
    assert generator.mode == "Local extractive"


def test_empty_question_is_rejected():
    generator = AnswerGenerator(api_key=None)
    try:
        generator.generate("", [])
        assert False, "Expected ValueError"
    except ValueError:
        pass
