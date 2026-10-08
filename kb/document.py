from dataclasses import dataclass, field

@dataclass
class Document:
    id: str
    title: str
    content: str
    node_path: str
    tags: list[str] = field(default_factory=list)