from dataclasses import dataclass
from kb.document import Document

@dataclass
class SearchResult:
    document: Document
    match_type: str = "unknown"