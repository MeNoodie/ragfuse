# Ragfuse

Ragfuse is a lightweight Python package for building Retrieval-Augmented Generation (RAG) pipelines. It helps you load files from common formats, split them into meaningful chunks, and generate embeddings for semantic search or downstream vector-based retrieval.

## Features

- Supports multiple document loaders: text, CSV, Excel, JSON, Markdown, and PDF
- Provides multiple chunking strategies: recursive, character-based, and contextual splitting
- Converts document chunks into sentence-transformer embeddings
- Keeps document metadata attached to each chunk for downstream use
- Small, dependency-light API focused on practical RAG workflows

## Installation

```bash
pip install ragfuse
```

## Quick start

```python
from ragfuse.betaworker import betaworker, alphaworker

chunks = betaworker(
    file_path="example.pdf",
    loader="pdf",
    chunker="recursive",
    chunk_size=1000,
    chunk_overlap=200,
)

embeddings = alphaworker(
    chunks=chunks,
    model="minilm",
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)

print(len(chunks))
print(len(embeddings))
```

## Supported loaders

| Loader name | File types | Notes |
| --- | --- | --- |
| `text` / `txt` | `.txt` | Plain text files |
| `csv` | `.csv` | Row-based document extraction |
| `excel` / `xls` / `xlsx` / `xlsm` | `.xls`, `.xlsx`, etc. | Row-based spreadsheet loading |
| `json` | `.json` | Uses JSON content with jq-style path selection |
| `markdown` / `md` | `.md` | Markdown documents loaded as content |
| `pdf` | `.pdf` | PDF page extraction |

## Supported chunkers

- `recursive`: best for general-purpose splitting with balanced chunk lengths
- `character` / `char`: fixed-size character chunking
- `contextual` / `context`: sentence-aware and paragraph-aware chunking

## Supported embedders

- `minilm`: sentence-transformers all-MiniLM-L6-v2 model

## Core API

### `betaworker(...)`

This function loads a file, automatically detects the appropriate loader based on the file extension, and splits the content into `Document` objects using the selected chunker.

```python
from ragfuse.betaworker import betaworker

chunks = betaworker(
    file_path="report.pdf",
    chunker="recursive",
    chunk_size=1000,
    chunk_overlap=200,
)
```

### `alphaworker(...)`

This function takes the chunked documents and generates one embedding per chunk using the selected embedding model.

```python
from ragfuse.betaworker import alphaworker

vectors = alphaworker(chunks=chunks, model="minilm")
```

## Document model

Each document is represented by the `Document` dataclass, which stores the page content and metadata:

```python
from ragfuse.betaworker import Document

item = Document(
    page_content="Hello world",
    metadata={"source": "example.txt"},
)
```

## Notes

- The default chunk configuration is `chunk_size=1000` and `chunk_overlap=200`.
- The chunk overlap must be smaller than the chunk size.
- If no loader is specified, Ragfuse picks one from the file extension automatically.

## Example workflow

```python
from ragfuse.betaworker import betaworker, alphaworker

chunks = betaworker("notes.md", chunker="contextual")
embeddings = alphaworker(chunks)

for idx, chunk in enumerate(chunks[:3]):
    print(f"Chunk {idx}: {chunk.page_content[:120]}")
    print(f"Embedding length: {len(embeddings[idx])}")
```

This package is designed to keep the RAG setup small and understandable while still supporting the most common data-loading and chunking workflows.