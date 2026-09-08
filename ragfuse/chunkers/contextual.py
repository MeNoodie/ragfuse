from .base import BaseChunker

class ContextualChunker(BaseChunker):
    """Group paragraphs and sentences without splitting logical boundaries."""

    def __init__(self, chunk_size=1000, chunk_overlap=200):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be non-negative and smaller than chunk_size"
            )
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_documents(self, documents):
        chunks = []
        for document in documents:
            for text in self._split_text(document.page_content):
                chunks.append(
                    type(document)(
                        page_content=text,
                        metadata=document.metadata.copy(),
                    )
                )
        return chunks

    def _split_text(self, text):
        paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
        units = []
        for paragraph in paragraphs:
            if len(paragraph) <= self.chunk_size:
                units.append(paragraph)
            else:
                units.extend(self._split_sentences(paragraph))

        chunks = []
        current = []
        current_length = 0
        for unit in units:
            separator_length = 2 if current else 0
            if current and current_length + separator_length + len(unit) > self.chunk_size:
                chunks.append("\n\n".join(current))
                overlap = chunks[-1][-self.chunk_overlap :]
                current = [overlap, unit] if overlap else [unit]
                current_length = len(overlap) + 2 + len(unit) if overlap else len(unit)
            else:
                current.append(unit)
                current_length += separator_length + len(unit)

        if current:
            chunks.append("\n\n".join(current))
        return chunks

    def _split_sentences(self, paragraph):
        sentences = []
        remaining = paragraph.strip()
        while len(remaining) > self.chunk_size:
            boundary = max(
                remaining.rfind(". ", 0, self.chunk_size),
                remaining.rfind("! ", 0, self.chunk_size),
                remaining.rfind("? ", 0, self.chunk_size),
            )
            if boundary <= 0:
                boundary = self.chunk_size
            else:
                boundary += 1
            sentences.append(remaining[:boundary].strip())
            remaining = remaining[boundary:].strip()
        if remaining:
            sentences.append(remaining)
        return sentences