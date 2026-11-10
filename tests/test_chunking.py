from app.preprocessing.text_chunker import TextChunker


def test_chunk_overlap_and_metadata():
    chunker = TextChunker(chunk_size=4, overlap=1)
    chunks = chunker.chunk_text("one two three four five six seven eight", "manual.pdf", 3)
    assert len(chunks) == 3
    assert chunks[0].text == "one two three four"
    assert chunks[1].text == "four five six seven"
    assert chunks[0].filename == "manual.pdf"
    assert chunks[0].page_number == 3


def test_empty_text_has_no_chunks():
    assert TextChunker().chunk_text("   ", "empty.pdf", 1) == []
