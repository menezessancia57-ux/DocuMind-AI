def format_citation(item: dict) -> str:
    return f"[{item['filename']}, page {item['page_number']}]"


def validate_citations(answer: str, evidence: list[dict]) -> list[str]:
    valid = []
    for item in evidence:
        citation = format_citation(item)
        if citation.lower() in answer.lower() and citation not in valid:
            valid.append(citation)
    return valid
