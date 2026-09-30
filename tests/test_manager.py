import pytest

from ticket_manager.manager import TicketManager
from ticket_manager.ticket import Ticket


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