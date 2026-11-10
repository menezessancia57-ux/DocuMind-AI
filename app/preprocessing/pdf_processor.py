from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from .text_cleaner import clean_text


@dataclass
class PDFDocument:
    filename: str
    pages: list[dict] = field(default_factory=list)
    error: str | None = None

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def character_count(self) -> int:
        return sum(len(page["text"]) for page in self.pages)


class PDFProcessingError(Exception):
    pass


class PDFProcessor:
    def __init__(self, max_upload_mb: int = 25):
        self.max_upload_mb = max_upload_mb

    def extract(self, source, filename: str | None = None) -> PDFDocument:
        try:
            import fitz
        except ImportError as exc:
            raise PDFProcessingError("PyMuPDF is required for PDF processing.") from exc

        if filename is None:
            filename = getattr(source, "name", Path(str(source)).name)
        if hasattr(source, "read"):
            source.seek(0) if hasattr(source, "seek") else None
            data = source.read()
        else:
            data = Path(source).read_bytes()
        if not data:
            raise PDFProcessingError("The uploaded PDF is empty.")
        if len(data) > self.max_upload_mb * 1024 * 1024:
            raise PDFProcessingError(f"PDF exceeds the {self.max_upload_mb} MB upload limit.")
        try:
            pdf = fitz.open(stream=data, filetype="pdf")
        except Exception as exc:
            raise PDFProcessingError("The file is not a readable PDF.") from exc
        if pdf.needs_pass:
            pdf.close()
            raise PDFProcessingError("The PDF is encrypted. Upload an unlocked copy.")
        try:
            pages = []
            for page_number, page in enumerate(pdf, start=1):
                text = clean_text(page.get_text("text"))
                pages.append({"page_number": page_number, "text": text})
            if not any(page["text"].strip() for page in pages):
                raise PDFProcessingError("No extractable text was found. The PDF may be scanned or image-only.")
            return PDFDocument(filename=filename, pages=pages)
        finally:
            pdf.close()
