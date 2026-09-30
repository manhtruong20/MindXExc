from ticket_manager.ticket import Ticket

class TicketManager:
    def __init__(self):
        self._tickets = {}

    def add(self, ticket):
        if not isinstance(ticket, Ticket):
            raise TypeError("Expected a Ticket")

        self._tickets[ticket.id] = ticket

    def get(self, ticket_id):
        return self._tickets.get(ticket_id)

    def ids(self):
        return list(self._tickets.keys())