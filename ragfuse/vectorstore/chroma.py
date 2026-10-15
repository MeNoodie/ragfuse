import os
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
        mode: str = "local",
    ) -> None:
        try:
            chromadb = import_module("chromadb")
        except ModuleNotFoundError as error:
            raise ImportError(
                "ChromaVectorStore requires chromadb. "
                "Install it with: pip install ragfuse[chroma]"
            ) from error

        if mode == "local":
            self._client = chromadb.PersistentClient(
                path=str(Path(persist_directory))
            )
        elif mode == "cloud":
            env_values = {
                "CHROMA_API_KEY": os.getenv("CHROMA_API_KEY"),
                "CHROMA_TENANT": os.getenv("CHROMA_TENANT"),
                "CHROMA_DATABASE": os.getenv("CHROMA_DATABASE"),
            }
            missing = [name for name, value in env_values.items() if not value]
            if missing:
                raise ValueError(
                    "Chroma Cloud requires these environment variables: "
                    f"{', '.join(missing)}"
                )

            config = {
                "api_key": env_values["CHROMA_API_KEY"],
                "tenant": env_values["CHROMA_TENANT"],
                "database": env_values["CHROMA_DATABASE"],
            }
            self._client = chromadb.CloudClient(**config)
        else:
            raise ValueError("mode must be either 'local' or 'cloud'")

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
