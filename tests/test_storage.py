import json

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


def test_load_returns_empty_manager_when_file_does_not_exist(tmp_path):
    assert load_tickets(tmp_path / "missing.json").ids() == []


def test_load_rejects_duplicate_ids(tmp_path):
    path = tmp_path / "tickets.json"
    record = {"id": "a1b2c3d4", "title": "T", "description": "D",
              "status": "Open", "priority": "High", "tags": []}
    path.write_text(json.dumps([record, record]))

    with pytest.raises(ValueError, match="a1b2c3d4"):
        load_tickets(path)