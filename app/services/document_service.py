import hashlib
from ..preprocessing.pdf_processor import PDFProcessor
from ..preprocessing.text_chunker import TextChunker


class DocumentService:
    def __init__(self, max_upload_mb: int = 25, chunk_size: int = 450, overlap: int = 75):
        self.processor = PDFProcessor(max_upload_mb=max_upload_mb)
        self.chunker = TextChunker(chunk_size=chunk_size, overlap=overlap)

    def process(self, uploaded_file, filename: str | None = None) -> dict:
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)
        content = uploaded_file.read()
        document_id = hashlib.sha256(content).hexdigest()
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)
        document = self.processor.extract(
            uploaded_file,
            filename or getattr(uploaded_file, "name", "document.pdf"),
        )
        chunks = self.chunker.chunk_pages(document.pages, document.filename)
        for chunk in chunks:
            chunk["document_id"] = document_id
        return {
            "document_id": document_id,
            "filename": document.filename,
            "pages": document.pages,
            "page_count": document.page_count,
            "character_count": document.character_count,
            "chunks": chunks,
        }
