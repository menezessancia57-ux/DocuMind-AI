import io
import fitz
import pytest

from app.preprocessing.pdf_processor import PDFProcessor, PDFProcessingError
from app.preprocessing.text_cleaner import clean_text


def test_clean_text():
    assert clean_text("  Hello\r\n\r\n  world   ") == "Hello\n\nworld"


def test_extract_pdf(tmp_path):
    path = tmp_path / "sample.pdf"
    pdf = fitz.open()
    page = pdf.new_page()
    page.insert_text((72, 72), "Natural language processing helps search documents.")
    pdf.save(path)
    pdf.close()
    result = PDFProcessor().extract(path)
    assert result.filename == "sample.pdf"
    assert result.page_count == 1
    assert "Natural language" in result.pages[0]["text"]


def test_scanned_pdf_is_reported(tmp_path):
    path = tmp_path / "scanned.pdf"
    pdf = fitz.open()
    pdf.new_page()
    pdf.save(path)
    pdf.close()
    with pytest.raises(PDFProcessingError, match="No extractable text"):
        PDFProcessor().extract(path)


def test_invalid_pdf():
    with pytest.raises(PDFProcessingError, match="readable PDF"):
        PDFProcessor().extract(io.BytesIO(b"not a pdf"), "bad.pdf")
