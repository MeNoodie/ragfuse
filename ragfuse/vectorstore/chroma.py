from importlib import import_module
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
from uuid import uuid4


class ChromaVectorStore:
    """Persist and query Ragfuse chunks with a local Chroma collection."""

    def __init__(
        self,
        persist_directory: str = "./local_vsdb",
        collection_name: str = "ragfuse",
    ) -> None:
        try:
            chromadb = import_module("chromadb")
        except ModuleNotFoundError as error:
            raise ImportError(
                "ChromaVectorStore requires chromadb. "
                "Install it with: pip install ragfuse[chroma]"
            ) from error

        self._client = chromadb.PersistentClient(path=str(Path(persist_directory)))
        self._collection = self._client.get_or_create_collection(
            name=collection_name
        )

    def upsert(
        self,
        chunks: Sequence[Any],
        embeddings: Sequence[Sequence[float]],
        ids: Optional[Sequence[str]] = None,
    ) -> List[str]:
        """Store chunks and their precomputed embeddings, returning their IDs."""
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length")
        if not chunks:
            return []

        record_ids = list(ids) if ids is not None else [
            uuid4().hex for _ in chunks
        ]
        if len(record_ids) != len(chunks):
            raise ValueError("ids and chunks must have the same length")

        self._collection.upsert(
            ids=record_ids,
            documents=[chunk.page_content for chunk in chunks],
            metadatas=[dict(chunk.metadata) for chunk in chunks],
            embeddings=[list(embedding) for embedding in embeddings],
        )
        return record_ids

    def query(
        self,
        embedding: Sequence[float],
        n_results: int = 5,
    ) -> Dict[str, Any]:
        """Find the nearest stored chunks for a precomputed query embedding."""
        if n_results <= 0:
            raise ValueError("n_results must be greater than zero")

        return self._collection.query(
            query_embeddings=[list(embedding)],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )