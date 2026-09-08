from abc import ABC, abstractmethod


class BaseChunker(ABC):
    """Define the interface implemented by every document chunker."""

    @abstractmethod
    def split_documents(self, documents):
        pass