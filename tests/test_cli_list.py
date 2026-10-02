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


@pytest.mark.parametrize("flag, values", [
    ("--status", ["Open", "Opne"]),
    ("--priority", ["High", "Urgent"]),
])
def test_list_rejects_whole_command_when_one_value_is_bad(tmp_path, capsys, flag, values):
    path = tmp_path / "tickets.json"
    write_tickets(path, make_ticket("aaaa0001"))

    with pytest.raises(SystemExit) as exit_info:
        main(["--file", str(path), "list", flag, *values])

    assert exit_info.value.code == 2
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("flag, value", [("--status", "open"), ("--priority", "high")])
def test_list_filter_values_are_case_sensitive(tmp_path, flag, value):
    with pytest.raises(SystemExit) as exit_info:
        main(["--file", str(tmp_path / "t.json"), "list", flag, value])

    assert exit_info.value.code == 2


@pytest.mark.parametrize("flag", ["--status", "--priority"])
def test_list_filter_flag_needs_at_least_one_value(tmp_path, capsys, flag):
    with pytest.raises(SystemExit) as exit_info:
        main(["--file", str(tmp_path / "t.json"), "list", flag])

    assert exit_info.value.code == 2
    assert "expected at least one argument" in capsys.readouterr().err


def test_list_on_missing_file_reports_error(tmp_path, capsys):
    path = tmp_path / "tickets.json"

    code = main(["--file", str(path), "list"])

    captured = capsys.readouterr()
    assert code == 1
    assert "not found" in captured.err
    assert captured.out == ""
    assert not path.exists()


def test_list_on_corrupted_file_reports_error_and_keeps_file(tmp_path, capsys):
    path = tmp_path / "tickets.json"
    path.write_text("{not valid json")

    code = main(["--file", str(path), "list"])

    assert code == 1
    assert "corrupted" in capsys.readouterr().err
    assert path.read_text() == "{not valid json"


@pytest.mark.parametrize("tickets, extra_args", [
    ([], []),
    ([make_ticket("aaaa0001", status="Open")], ["--status", "Closed"]),
])
def test_list_says_when_nothing_matches(tmp_path, capsys, tickets, extra_args):
    path = tmp_path / "tickets.json"
    write_tickets(path, *tickets)

    code = main(["--file", str(path), "list", *extra_args])

    assert code == 0
    assert capsys.readouterr().out.strip() == "No tickets found"