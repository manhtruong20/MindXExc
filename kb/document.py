from dataclasses import asdict, dataclass, field

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

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            title=data["title"],
            content=data["content"],
            node_path=data["node_path"],
            tags=list(data["tags"]),
        )