class Ticket:
    def __init__(self, title, description, priority):
        self.title = title
        self.description = description
        self.priority = priority

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