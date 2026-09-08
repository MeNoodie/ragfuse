from pathlib import Path

from .base import BaseLoader
from ..betaworker.models import Document


class MarkdownLoader(BaseLoader):
    """Load a Markdown file as a single document while preserving its markup."""

    def load(self, file_path: str | Path) -> list[Document]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Markdown file not found: {path}")

        return [
            Document(
                page_content=path.read_text(encoding="utf-8"),
                metadata={"source": str(path), "file_name": path.name, "file_type": "markdown"},
            )
        ]
