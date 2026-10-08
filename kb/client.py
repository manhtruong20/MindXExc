from abc import ABC, abstractmethod

from kb.document import Document
from kb.search_result import SearchResult

class KBClient(ABC):
    @abstractmethod
    def search(self, query: str, top_k: int) -> list[SearchResult]:
        ...

    @abstractmethod
    def list_documents(self, node_path: str, limit: int) -> list[Document]:
        ...

    @abstractmethod
    def retrieve(self, doc_id: str) -> Document:
        ...

    @abstractmethod
    def add(
        self, title: str, content: str, node_path: str, tags: list[str]
    ) -> Document:
        ...