from pathlib import Path
from .base import BaseLoader
from ..betaworker.models import Document


class PDFLoader(BaseLoader):
    """Load PDF pages with pypdf, preserving page metadata."""

    def load(self, file_path: str | Path) -> list[Document]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {path}")

        try:
            from pypdf import PdfReader
        except ModuleNotFoundError as error:
            raise ImportError(
                "PDFLoader requires pypdf. Install it with: pip install pypdf"
            ) from error

        reader = PdfReader(str(path))
        documents = []
        for page_number, page in enumerate(reader.pages):
            documents.append(
                Document(
                    page_content=page.extract_text() or "",
                    metadata={
                        "source": str(path),
                        "file_name": path.name,
                        "file_type": "pdf",
                        "page": page_number,
                    },
                )
            )
        return documents
