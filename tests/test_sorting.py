from ticket_manager.sorting import sort_groups
from ticket_manager.ticket import Ticket


def make_ticket(ticket_id, priority="High", status="Open"):
    return Ticket.from_dict({
        "id": ticket_id,
        "title": f"Ticket {ticket_id}",
        "description": "Some description",
        "status": status,
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


def test_second_rule_splits_inside_groups_without_mixing_them():
    t1 = make_ticket("aaaa0001", "High", "Open")
    t2 = make_ticket("aaaa0002", "Low", "Closed")
    t3 = make_ticket("aaaa0003", "High", "Closed")
    t4 = make_ticket("aaaa0004", "Low", "Open")
    rank = {"Low": 0, "Medium": 1, "High": 2}

    by_priority = sort_groups([[t1, t2, t3, t4]], key=lambda t: rank[t.priority])
    by_status = sort_groups(by_priority, key=lambda t: t.status)

    assert by_status == [[t2], [t4], [t3], [t1]]


def test_reverse_orders_buckets_descending_and_keeps_insertion_order_in_ties():
    t1 = make_ticket("aaaa0001", "Low")
    t2 = make_ticket("aaaa0002", "High")
    t3 = make_ticket("aaaa0003", "Low")
    rank = {"Low": 0, "Medium": 1, "High": 2}

    result = sort_groups([[t1, t2, t3]], key=lambda t: rank[t.priority], reverse=True)

    assert result == [[t2], [t1, t3]]