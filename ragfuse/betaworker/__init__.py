"""BetaWorker turns files into RAG-ready document chunks.

Loaders: text, CSV, Excel, JSON, PDF, and Markdown.
Chunkers: recursive.
"""

from .models import Document

__all__ = [
    "betaworker",
    "Document",
]


def __getattr__(name: str):
    if name == "betaworker":
        from .api import betaworker

        return betaworker
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
