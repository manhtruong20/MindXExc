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


def test_filter_by_priority():
    t1 = make_ticket("aaaa0001", priority="High")
    t2 = make_ticket("aaaa0002", priority="Low")
    t3 = make_ticket("aaaa0003", priority="High")

    result = filter_tickets([t1, t2, t3], priority=["High"])

    assert result == [t1, t3]

def test_filter_by_several_priorities():
    t1 = make_ticket("aaaa0001", priority="High")
    t2 = make_ticket("aaaa0002", priority="Low")
    t3 = make_ticket("aaaa0003", priority="Medium")

    result = filter_tickets([t1, t2, t3], priority=["High", "Medium"])

    assert result == [t1, t3]

def test_filter_by_tags_requires_all_of_them():
    t1 = make_ticket("aaaa0001", tags=["printer", "office"])
    t2 = make_ticket("aaaa0002", tags=["printer"])
    t3 = make_ticket("aaaa0003")

    result = filter_tickets([t1, t2, t3], tags=["printer", "office"])

    assert result == [t1]


def test_filter_with_empty_tags_returns_everything():
    t1 = make_ticket("aaaa0001", tags=["printer"])
    t2 = make_ticket("aaaa0002")

    assert filter_tickets([t1, t2], tags=[]) == [t1, t2]


def test_filter_with_no_match_returns_empty_list():
    t1 = make_ticket("aaaa0001", status="Open")

    assert filter_tickets([t1], status=["Closed"]) == []

def test_filter_combines_status_and_priority():
    t1 = make_ticket("aaaa0001", status="Open", priority="High")
    t2 = make_ticket("aaaa0002", status="Open", priority="Low")
    t3 = make_ticket("aaaa0003", status="Closed", priority="High")

    result = filter_tickets([t1, t2, t3], status=["Open"], priority=["High"])

    assert result == [t1]