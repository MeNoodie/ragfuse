# Ragfuse

**Add retrieval-augmented generation (RAG) capabilities to your Python application in a few steps.**

Ragfuse helps you load documents, split them into chunks, generate embeddings, and store those vectors locally with ChromaDB. Use the retrieved text as context in your own application or with your preferred language model.

## Features

- Load text, CSV, Excel, JSON, Markdown, and PDF documents
- Split documents with recursive, character-based, or contextual chunking
- Generate embeddings with sentence-transformers
- Persist and query vectors in a local ChromaDB database

## 1. Install

Ragfuse requires Python 3.10 or newer.

Install Ragfuse with its optional ChromaDB dependency:

```bash
pip install "ragfuse[chroma]"
```

## 2. Prepare a document

Create a text file, for example `my_notes.txt`, and add content that you want to search. The example below loads that file and creates chunks from it.

## 3. Load and chunk the document

```python
from ragfuse import betaworker

chunks = betaworker(
    file_path="my_notes.txt",
    loader="text",
    chunker="contextual",
    chunk_size=200,
    chunk_overlap=50,
)

print(f"Total chunks: {len(chunks)}")
```

## 4. Generate embeddings

```python
from ragfuse import alphaworker

embeddings = alphaworker(chunks=chunks, model="minilm")
```

The first run may download the sentence-transformer model.

## 5. Save vectors locally with ChromaDB

```python
from ragfuse import deltaworker

vector_store = deltaworker(
    chunks=chunks,
    embeddings=embeddings,
    vectorstore="chromadb",
    persist_directory="./local_vsdb",
    collection_name="generalstore",
)
```

ChromaDB stores its data in `./local_vsdb`, so it remains available between runs.

## 6. Search for relevant text

```python
matches = vector_store.query(embeddings[0], n_results=1)
print(matches["documents"][0][0])
```

This example queries with the first chunk's embedding. In your application, embed the user's question with the same model and pass that embedding to `vector_store.query()` to find relevant chunks. Send the returned text to your language model as context for generating an answer.

## Run the repository demo

The repository includes a runnable end-to-end example in [`test/test.py`](test/test.py). From the repository root, run:

```bash
python test/test.py
```

The demo uses `test/perm.txt` and persists its local ChromaDB data under `test/local_vsdb`.

## Current vector database support

Ragfuse currently supports local vector storage with ChromaDB. Install it through the `chroma` extra shown above.
