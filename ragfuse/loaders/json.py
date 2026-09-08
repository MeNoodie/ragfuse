from pathlib import Path

from .base import BaseLoader
from ..betaworker.models import Document


class JSONLoader(BaseLoader):
    """Load JSON with LangChain and an optional jq extraction schema."""

    def __init__(self, jq_schema: str = "."):
        self.jq_schema = jq_schema

    def load(self, file_path: str | Path) -> list[Document]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {path}")

        try:
            from langchain_community.document_loaders import JSONLoader as LangChainJSONLoader
        except ModuleNotFoundError as error:
            raise ImportError(
                "JSONLoader requires langchain-community and jq. "
                "Install them with: pip install langchain-community jq"
            ) from error

        loader = LangChainJSONLoader(
            file_path=str(path),
            jq_schema=self.jq_schema,
            text_content=False,
        )
        return [
            Document(page_content=document.page_content, metadata=dict(document.metadata))
            for document in loader.load()
        ]
