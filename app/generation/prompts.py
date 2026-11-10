def build_rag_prompt(question: str, evidence: list[dict]) -> str:
    evidence_text = "\n\n".join(
        f"Source [{index}] ({item['filename']}, page {item['page_number']}):\n{item['text']}"
        for index, item in enumerate(evidence, start=1)
    )
    return (
        "Answer the user's question using only the evidence below. "
        "Use citations in the exact form [filename.pdf, page N]. "
        "If the evidence is insufficient, say exactly: The answer cannot be established from the uploaded documents.\n\n"
        f"Evidence:\n{evidence_text}\n\nQuestion: {question}\nAnswer:"
    )
