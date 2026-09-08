from abc import ABC, abstractmethod


class BaseLoader(ABC):
    """Common interface for converting a source file into RAG documents."""

    @abstractmethod
    def load(self, file_path: str):
        """Read ``file_path`` and return a list of package ``Document`` objects."""
        pass
