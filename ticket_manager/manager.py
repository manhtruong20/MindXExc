from ticket_manager.ticket import Ticket

class TicketManager:
    def __init__(self):
        self._tickets = {}

    def add(self, ticket):
        if not isinstance(ticket, Ticket):
            raise TypeError("Expected a Ticket")

        if ticket.id in self._tickets:
            raise ValueError(f"Ticket with id {ticket.id} already exists")

        self._tickets[ticket.id] = ticket

    def get(self, ticket_id):
        return self._tickets.get(ticket_id)

    def ids(self):
        return list(self._tickets.keys())

    def remove(self, ticket_id):
        if ticket_id not in self._tickets:
            raise KeyError(f"No ticket with id {ticket_id}")

        del self._tickets[ticket_id]

    def update(self, ticket_id, **fields):
        ticket = self._tickets[ticket_id]

        for name, value in fields.items():
            setattr(ticket, name, value)