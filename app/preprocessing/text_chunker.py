from dataclasses import dataclass, asdict


@dataclass
class Chunk:
    chunk_id: str
    text: str
    filename: str
    page_number: int


class TextChunker:
    def __init__(self, chunk_size: int = 450, overlap: int = 75):
        if chunk_size < 1:
            raise ValueError("chunk_size must be positive")
        if overlap < 0 or overlap >= chunk_size:
            raise ValueError("overlap must be non-negative and smaller than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, filename: str = "document.pdf", page_number: int = 1, start_index: int = 0) -> list[Chunk]:
        words = text.split()
        chunks = []
        position = 0
        local_index = start_index
        step = self.chunk_size - self.overlap
        while position < len(words):
            piece = words[position:position + self.chunk_size]
            if piece:
                chunks.append(Chunk(
                    chunk_id=f"{filename}::{page_number}::{local_index}",
                    text=" ".join(piece),
                    filename=filename,
                    page_number=page_number,
                ))
                local_index += 1
            position += step
        return chunks

    def chunk_pages(self, pages: list[dict], filename: str) -> list[dict]:
        output = []
        offset = 0
        for page in pages:
            chunks = self.chunk_text(page["text"], filename, page["page_number"], offset)
            output.extend(asdict(chunk) for chunk in chunks)
            offset += len(chunks)
        return output
