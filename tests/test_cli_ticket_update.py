from ticket_manager.cli import main
from ticket_manager.manager import TicketManager
from ticket_manager.storage import load_tickets, save_tickets
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


def test_update_changes_status_and_saves(tmp_path, capsys):
    path = tmp_path / "tickets.json"
    write_tickets(path, make_ticket("aaaa0001"), make_ticket("aaaa0002"))

    code = main(["--file", str(path), "update", "aaaa0001", "Pending"])

    manager = load_tickets(path)
    assert code == 0
    assert manager.get("aaaa0001").status == "Pending"
    assert manager.get("aaaa0002").status == "Open"
    assert "Pending" in capsys.readouterr().out