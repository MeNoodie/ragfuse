from .base import BaseLoader
from ..betaworker.models import Document


class TextLoader(BaseLoader):
    """Load a UTF-8 plain-text file as one RAG document."""

    def load(self, file_path: str):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
        except UnicodeDecodeError as error:
            raise ValueError(
                f"{file_path} is not UTF-8 text. Use loader='pdf' for PDF files."
            ) from error

        return [
            Document(
                page_content=text,
                metadata={
                    "source": file_path,
                    "type": "text",
                },
            )
        ]