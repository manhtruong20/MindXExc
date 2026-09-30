import time


def _fnv1a_32(data):
    hash_value = 0x811C9DC5
    for byte in data:
        hash_value ^= byte
        hash_value = (hash_value * 0x01000193) & 0xFFFFFFFF
    return hash_value


def _generate_ticket_id(title, description, priority, timestamp_ns):
    payload = f"{timestamp_ns}:{title}:{description}:{priority}".encode("utf-8")
    return f"{_fnv1a_32(payload):08x}"


class Ticket:
    def __init__(self, title, description, priority):
        self.title = title
        self.description = description
        self.priority = priority
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
        if value not in ["Low", "Medium", "High"]:
            raise ValueError("Priority must be one of: Low, Medium, High")
        self._priority = value