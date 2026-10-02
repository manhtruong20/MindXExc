import pytest
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


def refuse_to_prompt(monkeypatch):
    def fail(prompt=""):
        raise AssertionError(f"unexpected prompt: {prompt}")

    monkeypatch.setattr("builtins.input", fail)


def test_update_unknown_id_reports_error_and_keeps_file(tmp_path, capsys):
    path = tmp_path / "tickets.json"
    write_tickets(path, make_ticket("aaaa0001"))
    before = path.read_text()

    code = main(["--file", str(path), "update", "deadbeef", "Closed"])

    captured = capsys.readouterr()
    assert code == 1
    assert "deadbeef" in captured.err
    assert "not found" in captured.err
    assert captured.out == ""
    assert path.read_text() == before


def test_update_on_missing_file_reports_error_and_creates_nothing(tmp_path, capsys):
    path = tmp_path / "tickets.json"

    code = main(["--file", str(path), "update", "aaaa0001", "Closed"])

    captured = capsys.readouterr()
    assert code == 1
    assert "not found" in captured.err
    assert not path.exists()


def test_update_on_corrupted_file_reports_error_and_keeps_file(tmp_path, capsys):
    path = tmp_path / "tickets.json"
    path.write_text("{not valid json")

    code = main(["--file", str(path), "update", "aaaa0001", "Closed"])

    assert code == 1
    assert "corrupted" in capsys.readouterr().err
    assert path.read_text() == "{not valid json"