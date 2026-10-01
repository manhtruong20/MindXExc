import json
from pathlib import Path

from ticket_manager.manager import TicketManager
from ticket_manager.ticket import Ticket


def save_tickets(manager, path):
    records = [ticket.to_dict() for ticket in manager]
    Path(path).write_text(json.dumps(records, indent=2))


def load_tickets(path):
    path = Path(path)
    manager = TicketManager()

    if not path.exists():
        return manager

    records = json.loads(path.read_text())
    for record in records:
        manager.add(Ticket.from_dict(record))
    return manager