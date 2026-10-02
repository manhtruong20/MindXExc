from ticket_manager.sorting import sort_groups
from ticket_manager.ticket import Ticket


def make_ticket(ticket_id, priority="High"):
    return Ticket.from_dict({
        "id": ticket_id,
        "title": f"Ticket {ticket_id}",
        "description": "Some description",
        "status": "Open",
        "priority": priority,
        "tags": [],
    })


def test_sort_splits_one_group_into_ordered_groups():
    t1 = make_ticket("aaaa0001", "High")
    t2 = make_ticket("aaaa0002", "Low")
    t3 = make_ticket("aaaa0003", "High")
    rank = {"Low": 0, "Medium": 1, "High": 2}

    result = sort_groups([[t1, t2, t3]], key=lambda t: rank[t.priority])

    assert result == [[t2], [t1, t3]]


def test_sort_keeps_empty_group():
    assert sort_groups([[]], key=lambda t: t.priority) == [[]]