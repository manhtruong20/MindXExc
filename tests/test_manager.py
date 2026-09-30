import pytest

from ticket_manager.manager import TicketManager
from ticket_manager.ticket import Ticket

@pytest.fixture
def manager():
    return TicketManager()

@pytest.fixture
def ticket():
    return Ticket.from_dict({
        "id": "a1b2c3d4",
        "title": "Printer broken",
        "description": "The office printer does not work",
        "status": "Open",
        "priority": "High",
        "tags": [],
    })

@pytest.fixture
def other_ticket(ticket):
    return Ticket.from_dict({**ticket.to_dict(), "id": "deadbeef"})

def test_can_create_ticket_manager():
    manager = TicketManager()

    assert manager is not None
    assert manager.ids() == []


def test_can_add_and_get_ticket():
    manager = TicketManager()

    ticket = Ticket(
        title="Printer broken",
        description="The office printer does not work",
        priority="High",
    )

    manager.add(ticket)

    assert manager.get(ticket.id) is ticket

def test_cannot_add_non_ticket():
    manager = TicketManager()

    with pytest.raises(TypeError):
        manager.add({"id": "fake ticket"})

def test_cannot_add_ticket_with_duplicate_id(manager, ticket):
    manager.add(ticket)

    with pytest.raises(ValueError, match="a1b2c3d4"):
        manager.add(ticket)

def test_failed_duplicate_add_keeps_original_ticket(manager, ticket, other_ticket):
    manager.add(ticket)
    impostor = Ticket.from_dict({**other_ticket.to_dict(), "id": ticket.id})

    with pytest.raises(ValueError):
        manager.add(impostor)

    assert manager.get(ticket.id) is ticket

def test_get_returns_none_for_unknown_id(manager):
    assert manager.get("does-not-exist") is None


def test_ids_are_returned_in_insertion_order(manager, ticket, other_ticket):
    manager.add(other_ticket)
    manager.add(ticket)

    assert manager.ids() == [other_ticket.id, ticket.id]


def test_can_remove_ticket(manager, ticket):
    manager.add(ticket)

    manager.remove(ticket.id)

    assert manager.ids() == []
    assert manager.get(ticket.id) is None


def test_removing_a_ticket_keeps_the_others(manager, ticket, other_ticket):
    manager.add(ticket)
    manager.add(other_ticket)

    manager.remove(ticket.id)

    assert manager.ids() == [other_ticket.id]


def test_removing_nonexistent_ticket_raises_error(manager):
    with pytest.raises(KeyError, match="a1b2c3d4"):
        manager.remove("a1b2c3d4")