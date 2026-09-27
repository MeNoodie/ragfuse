"""Public API for Ragfuse's beta pipeline.

This package exposes the document model and the two main processing steps used in
RAG workflows:

- ``betaworker`` prepares a file for retrieval by loading it and splitting it
  into document chunks.
- ``alphaworker`` turns those chunks into vector embeddings for similarity
  search or retrieval ranking.
"""

from .models import Document

__all__ = [
    "betaworker",
    "alphaworker",
    "Document",
]


def __getattr__(name: str):
    if name == "betaworker":
        from .api import betaworker

        return betaworker
    if name == "alphaworker":
        from .api import alphaworker

        return alphaworker
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
