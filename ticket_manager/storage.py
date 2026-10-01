import json
from pathlib import Path

from ticket_manager.manager import TicketManager
from ticket_manager.ticket import Ticket


def save_tickets(manager, path):
    records = [ticket.to_dict() for ticket in manager]
    Path(path).write_text(json.dumps(records, indent=2))


def load_tickets(path):
    records = json.loads(Path(path).read_text())
    manager = TicketManager()
    for record in records:
        manager.add(Ticket.from_dict(record))
    return manager