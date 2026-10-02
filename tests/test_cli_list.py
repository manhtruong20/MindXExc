from ticket_manager.cli import main
from ticket_manager.manager import TicketManager
from ticket_manager.storage import save_tickets
from ticket_manager.ticket import Ticket
import pytest


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


def test_list_filters_by_status(tmp_path, capsys):
    path = tmp_path / "tickets.json"
    write_tickets(
        path,
        make_ticket("aaaa0001", status="Open"),
        make_ticket("aaaa0002", status="Closed"),
        make_ticket("aaaa0003", status="Pending"),
    )

    code = main(["--file", str(path), "list", "--status", "Open", "Pending"])

    assert code == 0
    assert printed_ids(capsys) == ["aaaa0001", "aaaa0003"]


def test_list_rejects_unknown_status(tmp_path):
    with pytest.raises(SystemExit) as exit_info:
        main(["--file", str(tmp_path / "t.json"), "list", "--status", "Opne"])

    assert exit_info.value.code == 2


def test_list_filters_by_priority(tmp_path, capsys):
    path = tmp_path / "tickets.json"
    write_tickets(
        path,
        make_ticket("aaaa0001", priority="High"),
        make_ticket("aaaa0002", priority="Low"),
        make_ticket("aaaa0003", priority="Medium"),
    )

    code = main(["--file", str(path), "list", "--priority", "High", "Medium"])

    assert code == 0
    assert printed_ids(capsys) == ["aaaa0001", "aaaa0003"]

def test_list_rejects_unknown_priority(tmp_path):
    with pytest.raises(SystemExit) as exit_info:
        main(["--file", str(tmp_path / "t.json"), "list", "--priority", "Urgent"])

    assert exit_info.value.code == 2