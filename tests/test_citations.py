from app.generation.citation_validator import format_citation, validate_citations


def test_citation_format():
    assert format_citation({"filename": "report.pdf", "page_number": 4}) == "[report.pdf, page 4]"


def test_validates_only_supported_citations():
    evidence = [{"filename": "report.pdf", "page_number": 4}, {"filename": "other.pdf", "page_number": 2}]
    answer = "The report explains this [report.pdf, page 4]."
    assert validate_citations(answer, evidence) == ["[report.pdf, page 4]"]
