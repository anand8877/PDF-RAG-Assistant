"""A small, inspectable RAG pipeline built without an orchestration framework."""

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass(frozen=True)
class RetrievedChunk:
    text: str
    source: str
    page: int | None
    score: float


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    """Split text into word-window chunks while preserving overlap."""
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size must be positive and overlap must be smaller than chunk_size")
    words = re.findall(r"\S+", text)
    chunks = []
    step = chunk_size - overlap
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + chunk_size])
        if chunk:
            chunks.append(chunk)
        if start + chunk_size >= len(words):
            break
    return chunks


class DocumentStore:
    """Extract, chunk, index, and retrieve passages from PDF documents."""

    def __init__(self, chunk_size: int = 900, overlap: int = 150) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap
        self._chunks: list[RetrievedChunk] = []
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None

    @property
    def chunks(self) -> list[RetrievedChunk]:
        return list(self._chunks)

    def add_text(self, text: str, source: str, page: int | None = None) -> None:
        for chunk in chunk_text(text, self.chunk_size, self.overlap):
            self._chunks.append(RetrievedChunk(chunk, source, page, 0.0))
        self._reindex()

    def add_pdf(self, path: str | Path) -> int:
        pdf_path = Path(path)
        reader = PdfReader(str(pdf_path))
        before = len(self._chunks)
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            self.add_text(text, pdf_path.name, page_number)
        return len(self._chunks) - before

    def add_pdfs(self, paths: Iterable[str | Path]) -> int:
        total = 0
        for path in paths:
            total += self.add_pdf(path)
        return total

    def _reindex(self) -> None:
        if not self._chunks:
            self._vectorizer = None
            self._matrix = None
            return
        self._vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self._matrix = self._vectorizer.fit_transform(chunk.text for chunk in self._chunks)

    def search(self, question: str, top_k: int = 4) -> list[RetrievedChunk]:
        if not question.strip() or not self._chunks or self._vectorizer is None:
            return []
        scores = cosine_similarity(self._vectorizer.transform([question]), self._matrix)[0]
        ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
        return [
            RetrievedChunk(self._chunks[index].text, self._chunks[index].source, self._chunks[index].page, float(score))
            for index, score in ranked[: max(0, top_k)]
        ]
