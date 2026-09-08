from pathlib import Path

from .base import BaseLoader
from ..betaworker.models import Document


class CSVLoader(BaseLoader):
    """Load a CSV file as one RAG document per data row using pandas."""

    def load(self, file_path: str | Path) -> list[Document]:
        return self.extract_from_csv(file_path)

    @staticmethod
    def extract_from_csv(file_path: str | Path) -> list[Document]:
        try:
            import pandas as pd
        except ModuleNotFoundError as error:
            raise ImportError(
                "CSVLoader requires pandas. Install it with: pip install pandas"
            ) from error

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV not found: {path}")

        df = pd.read_csv(path)
        documents: list[Document] = []

        for idx, row in df.iterrows():
            row_text = " | ".join(f"{col}: {row[col]}" for col in df.columns)
            documents.append(
                Document(
                    page_content=row_text,
                    metadata={
                        "source": str(path),
                        "file_name": path.name,
                        "file_type": "csv",
                        "row": idx,
                        "total_rows": len(df),
                    },
                )
            )

        return documents
