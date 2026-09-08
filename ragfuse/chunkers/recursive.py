from .base import BaseChunker


class RecursiveChunker(BaseChunker):
    """Split text recursively at paragraphs, lines, sentences, and spaces."""

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
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
        except Exception:
            return self._split_without_langchain(documents)

        splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ". ", " ", ""],
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        chunks = []

        for document in documents:
            for chunk_text in splitter.split_text(document.page_content):
                chunks.append(
                    type(document)(
                        page_content=chunk_text,
                        metadata=document.metadata.copy(),
                    )
                )

        return chunks

    def _split_without_langchain(self, documents):
        """Use a simple overlapping splitter if LangChain is unavailable."""
        step = self.chunk_size - self.chunk_overlap
        chunks = []
        for document in documents:
            text = document.page_content
            for start in range(0, len(text), step):
                chunk_text = text[start : start + self.chunk_size]
                if chunk_text:
                    chunks.append(
                        type(document)(
                            page_content=chunk_text,
                            metadata=document.metadata.copy(),
                        )
                    )
                if start + self.chunk_size >= len(text):
                    break
        return chunks
