from ..chunkers.character import CharacterChunker
from ..chunkers.contextual import ContextualChunker
from ..loaders.csv import CSVLoader
from ..loaders.excel import ExcelLoader
from ..loaders.json import JSONLoader
from ..loaders.md import MarkdownLoader
from ..loaders.pdf import PDFLoader
from ..loaders.text import TextLoader
from ..chunkers.recursive import RecursiveChunker


LOADER_REGISTRY = {
    "text": TextLoader,
    "txt": TextLoader,
    "csv": CSVLoader,
    "excel": ExcelLoader,
    "xls": ExcelLoader,
    "xlsx": ExcelLoader,
    "xlsm": ExcelLoader,
    "json": JSONLoader,
    "markdown": MarkdownLoader,
    "md": MarkdownLoader,
    "pdf": PDFLoader,
}


CHUNKER_REGISTRY = {
    "recursive": RecursiveChunker,
    "character": CharacterChunker,
    "char": CharacterChunker,
    "contextual": ContextualChunker,
    "context": ContextualChunker,
}
