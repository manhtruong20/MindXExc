from ticket_manager.filters import filter_tickets
from ticket_manager.ticket import Ticket


def make_ticket(ticket_id, status="Open", priority="High", tags=()):
    return Ticket.from_dict({
        "id": ticket_id,
        "title": f"Ticket {ticket_id}",
        "description": "Some description",
        "status": status,
        "priority": priority,
        "tags": list(tags),
    })


def test_filter_by_status():
    t1 = make_ticket("aaaa0001", status="Open")
    t2 = make_ticket("aaaa0002", status="Closed")
    t3 = make_ticket("aaaa0003", status="Open")

    result = filter_tickets([t1, t2, t3], status="Open")

    assert result == [t1, t3]


def test_filter_with_no_arguments_returns_everything():
    t1 = make_ticket("aaaa0001", status="Open")
    t2 = make_ticket("aaaa0002", status="Closed")

    result = filter_tickets([t1, t2])

    assert result == [t1, t2]

def test_filter_with_empty_status_list_returns_everything():
    t1 = make_ticket("aaaa0001", status="Open")
    t2 = make_ticket("aaaa0002", status="Closed")

    result = filter_tickets([t1, t2], status=[])

    assert result == [t1, t2]


def test_filter_by_several_statuses():
    t1 = make_ticket("aaaa0001", status="Open")
    t2 = make_ticket("aaaa0002", status="Closed")
    t3 = make_ticket("aaaa0003", status="Pending")

    result = filter_tickets([t1, t2, t3], status=["Open", "Pending"])

    assert result == [t1, t3]