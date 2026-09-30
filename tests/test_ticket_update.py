import pytest
from ticket_manager.ticket import Ticket


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

def test_update_changes_given_fields(ticket):
    ticket.update(
        title="Printer jammed",
        description="The paper tray is jammed",
        priority="Low",
        status="Pending",
        tags="printer urgent",
    )

    assert ticket.title == "Printer jammed"
    assert ticket.description == "The paper tray is jammed"
    assert ticket.priority == "Low"
    assert ticket.status == "Pending"
    assert ticket.tags == {"printer", "urgent"}


def test_update_only_changes_given_fields(ticket):
    ticket.update(status="Closed")

    assert ticket.status == "Closed"
    assert ticket.title == "Printer broken"
    assert ticket.priority == "High"


@pytest.mark.parametrize("field", ["id", "deadbeff"])
def test_update_rejects_unknown_or_immutable_fields(ticket, field):
    with pytest.raises(TypeError, match=f"'{field}'"):
        ticket.update(**{field: "x"})

    assert ticket.id == "a1b2c3d4"


@pytest.mark.parametrize(
    "field, bad_value, message",
    [
        ("priority", "InvalidPrio", "Priority must be one of"),
        ("status", "InvalidStatus", "Status must be one of"),
        ("title", "   ", "Title cannot be empty"),
    ],
)
def test_failed_update_changes_nothing(ticket, field, bad_value, message):
    with pytest.raises(ValueError, match=message):
        ticket.update(description="Changed", **{field: bad_value})

    assert ticket.description == "The office printer does not work"
    assert ticket.title == "Printer broken"
    assert ticket.priority == "High"
    assert ticket.status == "Open"