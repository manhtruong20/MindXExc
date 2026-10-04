"""End-to-end tests: every command runs as a real, separate process.

Unlike the other CLI tests (which call main(...) in-process), these go through
python -m ticket_manager, real stdin/stdout/stderr and real exit codes, with a
fresh temporary folder as the working directory.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run(cwd, *args, stdin=None):
    """Run `python -m ticket_manager <args>` in `cwd` and return the result.

    stdin=None means no input is available (closed stdin).
    A string is piped in as if the user typed it.
    """
    env = {**os.environ}
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"

    input_args = {"stdin": subprocess.DEVNULL} if stdin is None else {"input": stdin}
    return subprocess.run(
        [sys.executable, "-m", "ticket_manager", *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        **input_args,
    )


def create(cwd, title, priority="High", tags=()):
    result = run(
        cwd, "create",
        "--title", title,
        "--description", "Some description",
        "--priority", priority,
        "--tags", *tags,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def listed_ids(result):
    return [line.split()[0] for line in result.stdout.strip().splitlines()]


#main test codes

def test_ticket_lifecycle_across_separate_processes(tmp_path):
    created = run(
        tmp_path, "create",
        "--title", "Printer broken",
        "--description", "Office printer is down",
        "--priority", "High",
        "--tags", "printer", "office",
    )
    assert created.returncode == 0, created.stderr
    ticket_id = created.stdout.strip()
    assert len(ticket_id) == 8
    assert (tmp_path / "tickets.json").exists()

    listing = run(tmp_path, "list")
    assert listing.returncode == 0, listing.stderr
    assert ticket_id in listing.stdout
    assert "Printer broken" in listing.stdout

    shown = run(tmp_path, "show", ticket_id)
    assert shown.returncode == 0, shown.stderr
    for expected in ["Printer broken", "Office printer is down", "Open", "High", "office, printer"]:
        assert expected in shown.stdout

    updated = run(tmp_path, "update", ticket_id, "Pending")
    assert updated.returncode == 0, updated.stderr

    assert listed_ids(run(tmp_path, "list", "--status", "Pending")) == [ticket_id]
    assert run(tmp_path, "list", "--status", "Open").stdout.strip() == "No tickets found"
    assert "Pending" in run(tmp_path, "show", ticket_id).stdout


def test_file_option_uses_a_different_file(tmp_path):
    result = run(
        tmp_path, "--file", "work.json", "create",
        "--title", "Printer broken",
        "--description", "Office printer is down",
        "--priority", "High",
        "--tags",
    )

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "work.json").exists()
    assert not (tmp_path / "tickets.json").exists()

    shown = run(tmp_path, "--file", "work.json", "show", result.stdout.strip())
    assert "Printer broken" in shown.stdout


#filtering and sorting

def test_list_filters_and_sorts(tmp_path):
    low = create(tmp_path, "Monitor flickers", "Low", ["monitor"])
    high_printer = create(tmp_path, "Printer broken", "High", ["printer", "office"])
    medium_printer = create(tmp_path, "Printer slow", "Medium", ["printer"])
    high_other = create(tmp_path, "Keyboard sticky", "High", [])
    run(tmp_path, "update", medium_printer, "Closed")

    assert listed_ids(run(tmp_path, "list")) == [low, high_printer, medium_printer, high_other]
    assert listed_ids(run(tmp_path, "list", "--priority", "High")) == [high_printer, high_other]
    assert listed_ids(run(tmp_path, "list", "--tags", "printer", "office")) == [high_printer]
    assert listed_ids(run(tmp_path, "list", "--status", "Closed")) == [medium_printer]
    assert listed_ids(
        run(tmp_path, "list", "--priority", "High", "Medium", "--tags", "printer")
    ) == [high_printer, medium_printer]

    # High first, ties keep creation order
    assert listed_ids(run(tmp_path, "list", "--sort", "priority")) == [
        high_printer, high_other, medium_printer, low,
    ]
    # filtering happens before sorting
    assert listed_ids(
        run(tmp_path, "list", "--priority", "High", "Low", "--sort", "priority")
    ) == [high_printer, high_other, low]


def test_filtering_and_sorting_never_modify_the_file(tmp_path):
    create(tmp_path, "Printer broken", "High", ["printer"])
    create(tmp_path, "Monitor flickers", "Low")
    before = (tmp_path / "tickets.json").read_text()

    run(tmp_path, "list", "--status", "Open", "--sort", "priority", "status")
    run(tmp_path, "list", "--tags", "nothing")

    assert (tmp_path / "tickets.json").read_text() == before


#interactive create

def test_create_asks_for_missing_values_and_asks_again_after_a_bad_one(tmp_path):
    answers = "\n".join([
        "Printer broken",
        "Office printer is down",
        "Urgent",
        "High",
        "printer office",
    ]) + "\n"

    result = run(tmp_path, "create", stdin=answers)

    assert result.returncode == 0, result.stderr
    assert "Invalid priority" in result.stderr
    # Piped input is not echoed, so the id follows the last prompt on the same line
    ticket_id = result.stdout.split()[-1]
    shown = run(tmp_path, "show", ticket_id)
    for expected in ["Printer broken", "Office printer is down", "High", "office, printer"]:
        assert expected in shown.stdout


def test_create_does_not_ask_when_everything_is_given(tmp_path):
    result = run(
        tmp_path, "create",
        "--title", "Printer broken",
        "--description", "Office printer is down",
        "--priority", "High",
        "--tags",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == result.stdout.split()[-1]  # only the id was printed


def test_create_without_input_reports_error_and_writes_nothing(tmp_path):
    result = run(tmp_path, "create", "--title", "Printer broken")

    assert result.returncode == 1
    assert "cannot ask" in result.stderr
    assert "Traceback" not in result.stderr
    assert not (tmp_path / "tickets.json").exists()


#errors: exit code, message on stderr

@pytest.mark.parametrize("args, code, message", [
    (["list"], 1, "not found"),
    (["show", "deadbeef"], 1, "not found"),
    (["update", "deadbeef", "Closed"], 1, "not found"),
    (["update", "deadbeef", "Nope"], 2, "invalid choice"),
    (["update", "deadbeef"], 2, "required"),
    (["list", "--status", "Opne"], 2, "invalid choice"),
    (["list", "--priority", "Urgent"], 2, "invalid choice"),
    (["list", "--sort", "title"], 2, "invalid choice"),
    (["frobnicate"], 2, "invalid choice"),
    ([], 2, "required"),
])
def test_errors_on_a_missing_file_use_exit_codes_and_create_nothing(tmp_path, args, code, message):
    result = run(tmp_path, *args)

    assert result.returncode == code
    assert message in result.stderr
    assert "Traceback" not in result.stderr
    assert not (tmp_path / "tickets.json").exists()


@pytest.mark.parametrize("args", [
    ["list"],
    ["show", "aaaa0001"],
    ["update", "aaaa0001", "Closed"],
    ["create", "--title", "T", "--description", "D", "--priority", "High", "--tags"],
])
def test_corrupted_file_is_reported_and_never_overwritten(tmp_path, args):
    path = tmp_path / "tickets.json"
    path.write_text("{not valid json")

    result = run(tmp_path, *args)

    assert result.returncode == 1
    assert "corrupted" in result.stderr
    assert "Traceback" not in result.stderr
    assert path.read_text() == "{not valid json"


def test_unknown_id_leaves_existing_tickets_untouched(tmp_path):
    create(tmp_path, "Printer broken")
    before = (tmp_path / "tickets.json").read_text()

    shown = run(tmp_path, "show", "deadbeef")
    updated = run(tmp_path, "update", "deadbeef", "Closed")

    assert shown.returncode == 1 and "deadbeef" in shown.stderr
    assert updated.returncode == 1 and "deadbeef" in updated.stderr
    assert (tmp_path / "tickets.json").read_text() == before


#exit codes of successful commands

def test_successful_commands_exit_with_zero_even_when_nothing_matches(tmp_path):
    create(tmp_path, "Printer broken")

    result = run(tmp_path, "list", "--status", "Closed")

    assert result.returncode == 0
    assert result.stdout.strip() == "No tickets found"
    assert result.stderr == ""


#the installed command

@pytest.mark.skipif(shutil.which("tickets") is None, reason="tickets command is not installed")
def test_installed_tickets_command_works(tmp_path):
    result = subprocess.run(
        [shutil.which("tickets"), "list"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        timeout=30,
    )

    assert result.returncode == 1
    assert "not found" in result.stderr
    assert not (tmp_path / "tickets.json").exists()