import io
import re
import fitz  # PyMuPDF

def extract_pages(pdf_bytes: bytes) -> list[dict]:
    """Extract selectable text from each page. Page numbers are 1-based."""
    pages = []
    with fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf") as document:
        for page_num, page in enumerate(document, start=1):
            text = page.get_text("text").strip()
            text = re.sub(r"[ \t]+\n", "\n", text)
            text = re.sub(r"\n{3,}", "\n\n", text)
            pages.append({"page": page_num, "text": text})
    return pages

def chunk_pages(pages: list[dict], chunk_size: int = 1100, overlap: int = 180) -> list[dict]:
    """Split each page's text into overlapping character chunks while retaining page metadata."""
    chunks = []
    for page in pages:
        text = page["text"]
        if not text:
            continue
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            piece = text[start:end].strip()
            if piece:
                chunks.append({"page": page["page"], "text": piece})
            if end >= len(text):
                break
            start = max(end - overlap, start + 1)
    return chunks
