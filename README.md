# Ragfuse

Ragfuse is a Python toolkit for preparing documents for retrieval-augmented generation (RAG). It loads supported files, splits their contents into searchable chunks, creates embeddings, and stores the text and vectors in ChromaDB. Your application can retrieve relevant chunks and pass them to the language model you already use.

Ragfuse handles document preparation, embeddings, and vector search. You choose and call the language model separately.

## What is included

### Document loaders

`betaworker` supports these file types and loader names:

| File type | Loader name | Behavior |
|---|---|---|
| Plain text | `text` | Loads a UTF-8 text file |
| PDF | `pdf` | Loads PDF pages and keeps page metadata |
| CSV | `csv` | Converts each row into a document |
| Excel (`.xls`, `.xlsx`, `.xlsm`) | `excel` | Converts each worksheet row into a document |
| JSON | `json` | Loads JSON content; the loader also supports a `jq_schema` when used directly |
| Markdown | `markdown` | Loads the Markdown file while preserving its markup |

The loader is detected from the file extension by default. You can pass `loader=` to choose it explicitly.

### Chunking strategies

Pass one of these registered names as `chunker=`:

- `recursive` (default): splits at paragraph, line, sentence, then character boundaries.
- `character`: splits text into character-sized pieces.
- `contextual`: groups paragraphs and sentences to keep logical text units together where possible.

`chunk_size` and `chunk_overlap` configure chunk length and repeated text between neighboring chunks. These sizes are measured in characters, not tokens. Chunk metadata such as source file and PDF page is carried onto the resulting chunks.

### Embeddings

`alphaworker` currently supports the `minilm` embedder, using `sentence-transformers/all-MiniLM-L6-v2` by default. It returns one vector per input chunk. You can pass a different Sentence Transformers model with `model_name=`. Use the same model for indexing documents and embedding search queries.

### Vector storage

`deltaworker` supports ChromaDB in two connection modes:

- Local persistent ChromaDB (`mode="local"`, the default)
- Chroma Cloud (`mode="cloud"`)

Both modes store chunk IDs, text, metadata, and the embeddings you provide. `upsert` with an existing ID updates that record. Other vector database backends are not currently included.

## Install

Ragfuse requires Python 3.10 or newer. Install Ragfuse with ChromaDB support:

```bash
pip install "ragfuse[chroma]"
```

This installs the package's base dependencies and the optional ChromaDB dependency. If you install just `pip install ragfuse`, ChromaDB must already be installed separately before you use the Chroma vector store.

## Quickstart: build a RAG pipeline

This example reads a text file, creates chunks and embeddings, stores them locally, retrieves relevant text for a question, and passes that context to your language model.

### 1. Prepare and embed a document

Create `knowledge.txt` with text you want your application to search, then run:

```python
from ragfuse import alphaworker, betaworker, deltaworker

# Load the file and split it into overlapping chunks.
chunks = betaworker(
    file_path="knowledge.txt",
    chunker="recursive",
    chunk_size=800,
    chunk_overlap=120,
)

# Make one vector embedding for each chunk.
embeddings = alphaworker(chunks=chunks, model="minilm")

# Save text, metadata, and embeddings in a persistent local Chroma collection.
vector_store = deltaworker(
    chunks=chunks,
    embeddings=embeddings,
    vectorstore="chroma",
    mode="local",
    persist_directory="./local_vsdb",
    collection_name="knowledge",
)

print(f"Indexed {len(chunks)} chunks")
```

### 2. Retrieve relevant chunks for a question

Create an embedding for the question using the same model, then search the collection:

```python
from ragfuse import Document, alphaworker, ChromaVectorStore

question = "What does the document say about our refund policy?"

query_embedding = alphaworker(
    chunks=[Document(page_content=question)],
    model="minilm",
)[0]

# Reopen the same persistent collection. This also works in a later process.
vector_store = ChromaVectorStore(
    persist_directory="./local_vsdb",
    collection_name="knowledge",
    mode="local",
)

results = vector_store.query(query_embedding, n_results=4)
matched_chunks = results["documents"][0]
context = "\n\n".join(matched_chunks)

print(context)
```

The results also include `metadatas` and `distances`. The `documents` value is grouped by query, so `[0]` selects the matches for this one question.

### 3. Ask your language model using the retrieved context

Ragfuse does not make the language-model call. Pass the retrieved context and question to your existing model client. For example, with a LangChain-compatible model object named `llm`:

```python
prompt = f"""Answer the question using only the context below.
If the answer is not in the context, say you could not find it.

Context:
{context}

Question: {question}
"""

response = llm.invoke(prompt)
print(response.content)
```

## Use a different loader or chunker

Choose a loader explicitly, or let Ragfuse infer it from the extension:

```python
pdf_chunks = betaworker(
    file_path="manual.pdf",
    loader="pdf",
    chunker="contextual",
    chunk_size=1000,
    chunk_overlap=150,
)

csv_chunks = betaworker(
    file_path="products.csv",
    chunker="character",
    chunk_size=500,
    chunk_overlap=50,
)
```

## Use Chroma Cloud

Create a `.env` file in your application with your Chroma Cloud connection details:

```env
CHROMA_API_KEY=your-api-key
CHROMA_TENANT=your-tenant
CHROMA_DATABASE=your-database
```

Python does not load `.env` files automatically. Load it in your application before calling Ragfuse, for example with `python-dotenv`:

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
from ragfuse import deltaworker

load_dotenv()

vector_store = deltaworker(
    chunks=chunks,
    embeddings=embeddings,
    vectorstore="chroma",
    mode="cloud",
    collection_name="knowledge",
)
```

To search later, construct `ChromaVectorStore` with the same `mode="cloud"` and collection name. Keep API keys in environment configuration or a secrets manager; do not commit them to source control.

## Updating indexed chunks

Pass stable IDs to `deltaworker` when indexing. Upserting a chunk with the same ID replaces its stored text, metadata, and embedding:

```python
ids = [f"knowledge-{index}" for index in range(len(chunks))]

vector_store = deltaworker(
    chunks=chunks,
    embeddings=embeddings,
    ids=ids,
    collection_name="knowledge",
)
```

For a targeted update, create a new chunk and embedding, then call `upsert` on the store with the same ID as the old record:

```python
updated_chunk = Document(
    page_content="The company address is 25 Market Street, Pune.",
    metadata={"source": "company details"},
)
updated_embedding = alphaworker([updated_chunk], model="minilm")[0]

vector_store.upsert(
    chunks=[updated_chunk],
    embeddings=[updated_embedding],
    ids=["company-address"],
)
```

## API overview

- `betaworker(file_path, loader, chunker, chunk_size, chunk_overlap)` loads and chunks a file.
- `alphaworker(chunks, model, model_name)` generates embeddings.
- `deltaworker(chunks, embeddings, vectorstore, mode, ...)` writes chunks and embeddings to Chroma and returns a store instance.
- `ChromaVectorStore(...).query(embedding, n_results=5)` retrieves similar chunks from an existing collection.

For local Chroma, Ragfuse writes data under `persist_directory` (default `./local_vsdb`). For Chroma Cloud, set the three `CHROMA_*` environment variables and use `mode="cloud"` for both indexing and querying.
