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
        self._title = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        if value not in ["Low", "Medium", "High"]:
            raise ValueError("Priority must be one of: Low, Medium, High")
        self._priority = value