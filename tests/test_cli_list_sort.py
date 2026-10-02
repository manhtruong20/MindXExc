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


def test_list_without_sort_keeps_insertion_order(tmp_path, capsys):
    path = tmp_path / "tickets.json"
    write_tickets(
        path,
        make_ticket("aaaa0001", priority="Low"),
        make_ticket("aaaa0002", priority="High"),
    )

    main(["--file", str(path), "list"])

    assert printed_ids(capsys) == ["aaaa0001", "aaaa0002"]


def test_list_sort_keeps_insertion_order_when_all_priorities_tie(tmp_path, capsys):
    path = tmp_path / "tickets.json"
    write_tickets(
        path,
        make_ticket("aaaa0003", priority="High"),
        make_ticket("aaaa0001", priority="High"),
        make_ticket("aaaa0002", priority="High"),
    )

    main(["--file", str(path), "list", "--sort", "priority"])

    assert printed_ids(capsys) == ["aaaa0003", "aaaa0001", "aaaa0002"]


def test_list_sorts_only_the_filtered_tickets(tmp_path, capsys):
    path = tmp_path / "tickets.json"
    write_tickets(
        path,
        make_ticket("aaaa0001", status="Open", priority="Low"),
        make_ticket("aaaa0002", status="Closed", priority="High"),
        make_ticket("aaaa0003", status="Open", priority="High"),
    )

    main(["--file", str(path), "list", "--status", "Open", "--sort", "priority"])

    assert printed_ids(capsys) == ["aaaa0003", "aaaa0001"]


def test_list_sort_with_no_matches_says_so(tmp_path, capsys):
    path = tmp_path / "tickets.json"
    write_tickets(path, make_ticket("aaaa0001", status="Open"))

    code = main(["--file", str(path), "list", "--status", "Closed", "--sort", "priority"])

    assert code == 0
    assert capsys.readouterr().out.strip() == "No tickets found"


def test_list_repeating_a_sort_rule_changes_nothing(tmp_path, capsys):
    path = tmp_path / "tickets.json"
    write_tickets(
        path,
        make_ticket("aaaa0001", priority="Low"),
        make_ticket("aaaa0002", priority="High"),
    )

    main(["--file", str(path), "list", "--sort", "priority", "priority"])

    assert printed_ids(capsys) == ["aaaa0002", "aaaa0001"]


def test_list_sort_never_modifies_the_file(tmp_path):
    path = tmp_path / "tickets.json"
    write_tickets(
        path,
        make_ticket("aaaa0001", priority="Low"),
        make_ticket("aaaa0002", priority="High"),
    )
    before = path.read_text()

    main(["--file", str(path), "list", "--sort", "priority"])

    assert path.read_text() == before


def test_list_sort_on_missing_file_still_reports_error(tmp_path, capsys):
    path = tmp_path / "tickets.json"

    code = main(["--file", str(path), "list", "--sort", "priority"])

    captured = capsys.readouterr()
    assert code == 1
    assert "not found" in captured.err
    assert not path.exists()


@pytest.mark.parametrize("bad_rule", ["title", "Priority", "PRIORITY", ""])
def test_list_rejects_unknown_sort_rule(tmp_path, capsys, bad_rule):
    with pytest.raises(SystemExit) as exit_info:
        main(["--file", str(tmp_path / "t.json"), "list", "--sort", bad_rule])

    assert exit_info.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


def test_list_rejects_whole_command_when_one_sort_rule_is_bad(tmp_path, capsys):
    path = tmp_path / "tickets.json"
    write_tickets(path, make_ticket("aaaa0001"))

    with pytest.raises(SystemExit) as exit_info:
        main(["--file", str(path), "list", "--sort", "priority", "title"])

    assert exit_info.value.code == 2
    assert capsys.readouterr().out == ""


def test_list_sort_flag_needs_at_least_one_value(tmp_path, capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["--file", str(tmp_path / "t.json"), "list", "--sort"])

    assert exit_info.value.code == 2
    assert "expected at least one argument" in capsys.readouterr().err


def test_list_sorts_by_status_in_workflow_order(tmp_path, capsys):
    path = tmp_path / "tickets.json"
    write_tickets(
        path,
        make_ticket("aaaa0001", status="Closed"),
        make_ticket("aaaa0002", status="Open"),
        make_ticket("aaaa0003", status="Waiting"),
        make_ticket("aaaa0004", status="Pending"),
        make_ticket("aaaa0005", status="Resolved"),
    )

    main(["--file", str(path), "list", "--sort", "status"])

    assert printed_ids(capsys) == [
        "aaaa0002", "aaaa0004", "aaaa0003", "aaaa0005", "aaaa0001",
    ]


def test_list_second_sort_rule_breaks_ties_of_the_first(tmp_path, capsys):
    path = tmp_path / "tickets.json"
    write_tickets(
        path,
        make_ticket("aaaa0001", status="Closed", priority="High"),
        make_ticket("aaaa0002", status="Open", priority="Low"),
        make_ticket("aaaa0003", status="Open", priority="High"),
        make_ticket("aaaa0004", status="Closed", priority="Low"),
    )

    main(["--file", str(path), "list", "--sort", "priority", "status"])
    by_priority_first = printed_ids(capsys)

    main(["--file", str(path), "list", "--sort", "status", "priority"])
    by_status_first = printed_ids(capsys)

    assert by_priority_first == ["aaaa0003", "aaaa0001", "aaaa0002", "aaaa0004"]
    assert by_status_first == ["aaaa0003", "aaaa0002", "aaaa0001", "aaaa0004"]