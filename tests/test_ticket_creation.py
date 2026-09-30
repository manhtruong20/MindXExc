
import pytest

from ticket_manager.ticket import Ticket


def test_can_create_ticket():
    ticket = Ticket(
        title="Printer broken",
        description="The office printer does not work",
        priority="High",
    )
    assert ticket is not None

def test_ticket_attributes():
    ticket = Ticket(
        title="Printer broken",
        description="The office printer does not work",
        priority="High",
    )
    assert ticket.title == "Printer broken"
    assert ticket.description == "The office printer does not work"
    assert ticket.priority == "High"


def test_ticket_attributes_can_be_updated():
    ticket = Ticket(
        title="Printer broken",
        description="The office printer does not work",
        priority="High",
    )

    ticket.title = "Printer jammed"
    ticket.description = "The paper tray is jammed"
    ticket.priority = "Medium"

    assert ticket.title == "Printer jammed"
    assert ticket.description == "The paper tray is jammed"
    assert ticket.priority == "Medium"

@pytest.mark.parametrize("valid_priority", ["Low", "Medium", "High"])
def test_ticket_enforces_priority_values(valid_priority):
    ticket = Ticket(
        title="Printer broken",
        description="The office printer does not work",
        priority=valid_priority,
    )
    assert ticket.priority == valid_priority

    with pytest.raises(ValueError, match="Priority must be one of: Low, Medium, High"):
        ticket.priority = "Some invalid priority"