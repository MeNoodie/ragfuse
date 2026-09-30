from pathlib import Path

from .registry import (
    CHUNKER_REGISTRY,
    EMBEDDER_REGISTRY,
    LOADER_REGISTRY,
    VECTORSTORE_REGISTRY,
)


def betaworker(
    file_path: str,
    loader: str = None,
    chunker: str = "recursive",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
):
    """Load a file and split it into retrieval-ready document chunks.

    The pipeline is intentionally simple: detect the file type, choose the
    matching loader, transform the raw content into Ragfuse's ``Document``
    objects, and then split those documents into chunk-sized text blocks using a
    configured chunker.

    Supported loaders include plain text, CSV, Excel, JSON, Markdown, and PDF.
    Supported chunkers include recursive, character-based, and contextual
    splitting. The default settings create chunks of up to 1000 characters with
    a 200-character overlap between adjacent chunks.

    Args:
        file_path: Path to the source file to process.
        loader: Optional loader override. If omitted, Ragfuse detects the loader
            from the file extension.
        chunker: Name of the chunking strategy to use.
        chunk_size: Maximum number of characters in each chunk.
        chunk_overlap: Number of overlapping characters between neighboring
            chunks.

    Returns:
        A list of chunked ``Document`` objects ready for indexing or embedding.

    Raises:
        ValueError: If the loader or chunker name is unsupported, or if the file
            extension cannot be mapped to a registered loader.
    """
    # -------------------------
    # 1. Detect loader by file extension when no override is supplied.
    # -------------------------
    extension_to_loader = {
        "txt": "text",
        "csv": "csv",
        "pdf": "pdf",
        "json": "json",
        "md": "markdown",
        "xls": "excel",
        "xlsx": "excel",
        "xlsm": "excel",
    }

    if loader is None:
        suffix = Path(file_path).suffix.lower().lstrip(".")
        loader = extension_to_loader.get(suffix)

        if loader not in LOADER_REGISTRY:
            raise ValueError(f"Cannot detect loader for: {file_path}")

    # -------------------------
    # 2. Validate and create the loader.
    # -------------------------
    if loader not in LOADER_REGISTRY:
        raise ValueError(f"Unsupported loader: {loader}")

    loader_class = LOADER_REGISTRY[loader]
    loader_instance = loader_class()

    # -------------------------
    # 3. Load the source document(s).
    # -------------------------
    documents = loader_instance.load(file_path)

    # -------------------------
    # 4. Validate and initialize the chunker.
    # -------------------------
    if chunker not in CHUNKER_REGISTRY:
        raise ValueError(f"Unsupported chunker: {chunker}")

    chunker_class = CHUNKER_REGISTRY[chunker]
    chunker_instance = chunker_class(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    # -------------------------
    # 5. Split the loaded content into text chunks.
    # -------------------------
    chunks = chunker_instance.split_documents(documents)
    return chunks


def alphaworker(
    chunks: list,
    model: str = "minilm",
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
):
    """Generate embeddings for a list of Ragfuse document chunks.

    This utility converts each chunk's ``page_content`` into a vector using the
    selected embedding model. It is useful for turning retrieved passages into
    numeric representations that can be compared or indexed for semantic search.

    Args:
        chunks: A list of Ragfuse ``Document`` objects or chunk objects with a
            ``page_content`` attribute.
        model: Model registry key to use for embedding generation.
        model_name: Hugging Face model name passed to the selected embedder.

    Returns:
        A list of embedding vectors, with one vector per chunk.
    """
    embedder_class = EMBEDDER_REGISTRY[model]
    embedder = embedder_class(model_name=model_name)

    texts = [chunk.page_content for chunk in chunks]
    embeddings = embedder.embed_documents(texts)
    return embeddings


def deltaworker(
    chunks: list,
    embeddings: list,
    vectorstore: str = "chroma",
    persist_directory: str = "./local_vsdb",
    collection_name: str = "ragfuse",
    ids: list = None,
):
    """Store document chunks and their precomputed embeddings locally.

    Args:
        chunks: Ragfuse documents to store.
        embeddings: One embedding vector per chunk, usually from
            ``alphaworker``.
        vectorstore: Registered vector-store name (``chroma`` or ``chromadb``).
        persist_directory: Local directory where Chroma persists its database.
        collection_name: Name of the Chroma collection to create or reuse.
        ids: Optional stable IDs for updating existing records on re-indexing.

    Returns:
        The initialized vector-store instance, ready for queries.

    Raises:
        ValueError: If the vector-store name is not registered.
    """
    if vectorstore not in VECTORSTORE_REGISTRY:
        raise ValueError(f"Unsupported vector store: {vectorstore}")

    vectorstore_class = VECTORSTORE_REGISTRY[vectorstore]
    store = vectorstore_class(
        persist_directory=persist_directory,
        collection_name=collection_name,
    )
    store.upsert(chunks=chunks, embeddings=embeddings, ids=ids)
    return store
