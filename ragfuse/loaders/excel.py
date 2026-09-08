from pathlib import Path

from .base import BaseLoader
from ..betaworker.models import Document


class ExcelLoader(BaseLoader):
    """Load every worksheet in an Excel file as one RAG document per row."""

    def load(self, file_path: str | Path) -> list[Document]:
        return self.extract_from_excel(file_path)

    @staticmethod
    def extract_from_excel(file_path: str | Path) -> list[Document]:
        try:
            import pandas as pd
        except ModuleNotFoundError as error:
            raise ImportError(
                "ExcelLoader requires pandas. Install it with: pip install pandas openpyxl"
            ) from error

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Excel file not found: {path}")

        documents: list[Document] = []

        with pd.ExcelFile(path) as xls:
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                for idx, row in df.iterrows():
                    row_text = " | ".join(f"{col}: {row[col]}" for col in df.columns)
                    documents.append(
                        Document(
                            page_content=row_text,
                            metadata={
                                "source": str(path),
                                "file_name": path.name,
                                "file_type": "excel",
                                "sheet": sheet_name,
                                "row": idx,
                                "total_rows": len(df),
                            },
                        )
                    )

        return documents
