from .base import BaseChunker

class FixedChunker(BaseChunker):
    """Split an input sequence into fixed-size overlapping slices."""

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
        """ Simple fixed type chunking """
        step = self.chunk_size - self.chunk_overlap

        return [
            documents[start:start + self.chunk_size]
            for start in range(0,len(documents),step)
        ]