import io
import os
from typing import List, Tuple

import pdfplumber
from bs4 import BeautifulSoup
from docx import Document

from .text import clean_text


def extract_pdf(file_bytes: bytes) -> List[Tuple[int, str]]:
    pages = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = clean_text(page.extract_text() or "")
            if text:
                pages.append((i, text))
    return pages


def extract_docx(file_bytes: bytes) -> List[Tuple[int, str]]:
    doc = Document(io.BytesIO(file_bytes))
    full_text = "\n".join(p.text for p in doc.paragraphs)
    text = clean_text(full_text)
    return [(1, text)] if text else []


def extract_txt(file_bytes: bytes) -> List[Tuple[int, str]]:
    text = clean_text(file_bytes.decode("utf-8", errors="ignore"))
    return [(1, text)] if text else []


def extract_html(file_bytes: bytes) -> List[Tuple[int, str]]:
    soup = BeautifulSoup(file_bytes, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    text = clean_text(soup.get_text(" "))
    return [(1, text)] if text else []


def extract_transcript(file_bytes: bytes) -> List[Tuple[int, str]]:
    text = clean_text(file_bytes.decode("utf-8", errors="ignore"))
    return [(1, text)] if text else []


def detect_and_extract(filename: str, file_bytes: bytes) -> List[Tuple[int, str]]:
    ext = os.path.splitext(filename.lower())[1]
    if ext == ".pdf":
        return extract_pdf(file_bytes)
    if ext in {".docx"}:
        return extract_docx(file_bytes)
    if ext in {".txt", ".md"}:
        return extract_txt(file_bytes)
    if ext in {".html", ".htm"}:
        return extract_html(file_bytes)
    if ext in {".vtt", ".srt"}:
        return extract_transcript(file_bytes)
    return []
