import time
VALID_STATUSES = ("Open", "Pending", "Waiting", "Resolved", "Closed")
UPDATABLE_FIELDS = {"title", "description", "priority", "status", "tags"}
VALID_PRIORITIES = {"Low", "Medium", "High"}

def _fnv1a_32(data):
    hash_value = 0x811C9DC5
    for byte in data:
        hash_value ^= byte
        hash_value = (hash_value * 0x01000193) & 0xFFFFFFFF
    return hash_value


def _generate_ticket_id(title, description, priority, timestamp_ns):
    payload = f"{timestamp_ns}:{title}:{description}:{priority}".encode("utf-8")
    return f"{_fnv1a_32(payload):08x}"

def _validate_id(ticket_id):
    if not isinstance(ticket_id, str) or not ticket_id.strip():
        raise ValueError("Id cannot be empty or whitespace")


def _is_valid_tag(tag):
    if not isinstance(tag, str):
        return False
    if tag == "":
        return False
    return not any(char.isspace() for char in tag)


def _validate_tags(tags):
    if not isinstance(tags, list):
        raise ValueError("Tags must be a list")
    for tag in tags:
        if not _is_valid_tag(tag):
            raise ValueError(
                f"Tags must be non-empty strings without whitespace, got {tag!r}"
            )


class Ticket:
    def __init__(self, title, description, priority, tags=""):
        self.title = title
        self.description = description
        self.priority = priority
        self.status = "Open"
        self.tags = tags
        self._id = _generate_ticket_id(
            self.title,
            self.description,
            self.priority,
            time.time_ns(),
        )

    @property
    def id(self):
        return self._id

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, value):
        if not isinstance(value, str):
            raise TypeError("Tags must be a whitespace-separated string")
        self._tags = set(value.split())

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Title cannot be empty or whitespace")
        self._title = value[:100]

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Description cannot be empty or whitespace")
        self._description = value

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        if value not in VALID_PRIORITIES:
            raise ValueError("Priority must be one of: " + ", ".join(sorted(VALID_PRIORITIES)))
        self._priority = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value not in VALID_STATUSES:
            allowed = ", ".join(sorted(VALID_STATUSES))
            raise ValueError(f"Status must be one of: {allowed}")
        self._status = value

    @classmethod
    def blank(cls):
        return cls.__new__(cls)

    @classmethod
    def from_dict(cls, data):
        ticket = cls.blank()

        # id has no setter, so it is validated here
        _validate_id(data["id"])
        ticket._id = data["id"]

        ticket.title = data["title"]
        ticket.description = data["description"]
        ticket.priority = data["priority"]
        ticket.status = data["status"]

        tags = data.get("tags", [])
        _validate_tags(tags)
        ticket.tags = " ".join(tags)

        return ticket

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "tags": sorted(self.tags),
        }

    def update(self, **fields):
        unknown = set(fields) - UPDATABLE_FIELDS
        if unknown:
            names = ", ".join(repr(name) for name in sorted(unknown))
            raise TypeError(f"Cannot update field(s): {names}")

        candidate = Ticket.from_dict(self.to_dict())
        for name, value in fields.items():
            setattr(candidate, name, value)  # raises here, before self is touched

        self._title = candidate.title
        self._description = candidate.description
        self._priority = candidate.priority
        self._status = candidate.status
        self._tags = candidate.tags