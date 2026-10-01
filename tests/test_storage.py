import pytest

from ticket_manager.manager import TicketManager
from ticket_manager.storage import save_tickets, load_tickets
from ticket_manager.ticket import Ticket


@pytest.fixture
def manager():
    m = TicketManager()
    m.add(Ticket.from_dict({
        "id": "a1b2c3d4", "title": "First", "description": "d1",
        "status": "Open", "priority": "High", "tags": ["a", "b"],
    }))
    m.add(Ticket.from_dict({
        "id": "deadbeef", "title": "Second", "description": "d2",
        "status": "Closed", "priority": "Low", "tags": [],
    }))
    return m


def test_saved_manager_can_be_loaded_back(manager, tmp_path):
    path = tmp_path / "tickets.json"

    save_tickets(manager, path)
    loaded = load_tickets(path)

    assert [t.to_dict() for t in loaded] == [t.to_dict() for t in manager]