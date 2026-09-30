from ticket_manager.ticket import Ticket


def test_update_changes_given_fields():
    ticket = Ticket.from_dict({
        "id": "a1b2c3d4",
        "title": "Printer broken",
        "description": "The office printer does not work",
        "status": "Open",
        "priority": "High",
        "tags": [],
    })

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