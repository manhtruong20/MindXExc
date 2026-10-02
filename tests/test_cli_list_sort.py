import pytest

from ticket_manager.cli import main
from ticket_manager.manager import TicketManager
from ticket_manager.storage import save_tickets
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


def write_tickets(path, *tickets):
    manager = TicketManager()
    for ticket in tickets:
        manager.add(ticket)
    save_tickets(manager, path)


def printed_ids(capsys):
    lines = capsys.readouterr().out.strip().splitlines()
    return [line.split()[0] for line in lines]


def test_list_sorts_by_priority_highest_first(tmp_path, capsys):
    path = tmp_path / "tickets.json"
    write_tickets(
        path,
        make_ticket("aaaa0001", priority="Low"),
        make_ticket("aaaa0002", priority="High"),
        make_ticket("aaaa0003", priority="Medium"),
        make_ticket("aaaa0004", priority="High"),
    )

    code = main(["--file", str(path), "list", "--sort", "priority"])

    assert code == 0
    assert printed_ids(capsys) == ["aaaa0002", "aaaa0004", "aaaa0003", "aaaa0001"]