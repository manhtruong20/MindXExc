from dataclasses import dataclass, field

@dataclass
class Document:
    id: str
    title: str
    content: str
    node_path: str
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.id == "":
            raise ValueError("id must not be empty")