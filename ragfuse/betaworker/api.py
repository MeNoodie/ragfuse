from pathlib import Path

from .registry import LOADER_REGISTRY, CHUNKER_REGISTRY


def betaworker(
    file_path: str,
    loader: str = None,
    chunker: str = "recursive",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
):
    """Load a file and split it into RAG-ready document chunks.

    The loader is selected from ``loader`` or, when omitted, from the file
    extension. Each loader returns this package's ``Document`` objects, and
    the selected chunker preserves their metadata on every output chunk.

    Supported loaders:
        - ``text`` / ``txt``: UTF-8 plain-text files.
        - ``csv``: CSV files, one document per data row.
        - ``excel`` / ``xls`` / ``xlsx`` / ``xlsm``: Excel files, one document per row.
        - ``json``: JSON files loaded through LangChain and jq.
        - ``pdf``: PDF pages loaded through pypdf.
        - ``markdown`` / ``md``: Markdown files loaded as one document.

    Supported chunkers:
        - ``recursive``: LangChain RecursiveCharacterTextSplitter.
        - ``character`` / ``char``: fixed-size character splitting.
        - ``contextual`` / ``context``: paragraph and sentence-aware splitting.

    The default chunk configuration is ``chunk_size=1000`` and
    ``chunk_overlap=200``. All chunkers validate that the overlap is smaller
    than the chunk size.

    When ``loader`` is omitted, it is detected from the file extension. For example,
    ``report.pdf`` selects the ``pdf`` loader and ``data.csv`` selects ``csv``.

    Args:
        file_path: Path to the source file.
        loader: Optional loader name. Use it to override automatic detection.
        chunker: Chunker name. Defaults to ``recursive``.
        chunk_size: Maximum number of characters in each chunk. Defaults to 1000.
        chunk_overlap: Number of overlapping characters between chunks. Defaults to 200.

    Returns:
        A list of this package's chunked ``Document`` objects.
    """
    # -------------------------
    # 1. Detect loader
    # -------------------------

    if loader is None:

        suffix = Path(file_path).suffix.lower().lstrip(".")
        loader = "text" if suffix == "txt" else suffix

        if loader not in LOADER_REGISTRY:
            raise ValueError(
                f"Cannot detect loader for: {file_path}"
            )

    # -------------------------
    # 2. Get loader
    # -------------------------

    if loader not in LOADER_REGISTRY:
        raise ValueError(
            f"Unsupported loader: {loader}"
        )

    loader_class = LOADER_REGISTRY[loader]

    loader_instance = loader_class()

    # -------------------------
    # 3. Load document
    # -------------------------

    documents = loader_instance.load(file_path)

    # -------------------------
    # 4. Get chunker
    # -------------------------

    if chunker not in CHUNKER_REGISTRY:
        raise ValueError(
            f"Unsupported chunker: {chunker}"
        )

    chunker_class = CHUNKER_REGISTRY[chunker]

    chunker_instance = chunker_class(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    # -------------------------
    # 5. Chunk documents
    # -------------------------

    chunks = chunker_instance.split_documents(
        documents
    )

    return chunks
