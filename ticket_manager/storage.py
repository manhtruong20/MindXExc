import json
from pathlib import Path

from ticket_manager.manager import TicketManager
from ticket_manager.ticket import Ticket


def save_tickets(manager, path):
    records = [ticket.to_dict() for ticket in manager]
    Path(path).write_text(json.dumps(records, indent=2))


class StorageError(Exception):
    pass

def load_tickets(path):
    path = Path(path)
    manager = TicketManager()

    if not path.exists():
        return manager

    try:
        records = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        raise StorageError(f"Ticket file {path} is corrupted: {error}") from error

    if not isinstance(records, list):
        raise StorageError(
            f"Ticket file {path} is corrupted: expected a list of tickets"
        )

    for record in records:
        manager.add(Ticket.from_dict(record))
    return manager