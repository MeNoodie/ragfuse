from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Document:
    """Store document text together with source and format metadata."""

    page_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
