from ticket_manager.cli import main
from ticket_manager.storage import load_tickets
import pytest

@pytest.fixture(autouse=True)
def blank_answers_by_default(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "")


def test_show_on_missing_file_reports_error(tmp_path, capsys):
    path = tmp_path / "tickets.json"

    code = main(["--file", str(path), "show", "a1b2c3d4"])

    captured = capsys.readouterr()
    assert code == 1
    assert "not found" in captured.err
    assert not path.exists()


def test_create_saves_ticket_and_prints_its_id(tmp_path, capsys):
    path = tmp_path / "tickets.json"

    code = main([
        "--file", str(path),
        "create",
        "--title", "Printer broken",
        "--description", "The office printer does not work",
        "--priority", "High",
    ])

    printed_id = capsys.readouterr().out.strip()
    assert code == 0
    assert load_tickets(path).ids() == [printed_id]

def test_show_prints_ticket_details(tmp_path, capsys):
    path = tmp_path / "tickets.json"
    main(["--file", str(path), "create",
          "--title", "Printer broken",
          "--description", "The office printer does not work",
          "--priority", "High"])
    ticket_id = capsys.readouterr().out.strip()

    code = main(["--file", str(path), "show", ticket_id])

    out = capsys.readouterr().out
    assert code == 0
    assert ticket_id in out
    assert "Printer broken" in out
    assert "The office printer does not work" in out
    assert "High" in out
    assert "Open" in out


def test_create_prompts_for_missing_arguments(tmp_path, capsys, monkeypatch):
    path = tmp_path / "tickets.json"
    answers = iter([
        "Printer broken",
        "The office printer does not work",
        "High",
        "printer office",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))

    code = main(["--file", str(path), "create"])

    ticket = load_tickets(path).get(capsys.readouterr().out.strip())
    assert code == 0
    assert ticket.title == "Printer broken"
    assert ticket.description == "The office printer does not work"
    assert ticket.priority == "High"
    assert ticket.tags == {"printer", "office"}


def test_create_does_not_prompt_for_arguments_already_given(tmp_path, monkeypatch):
    path = tmp_path / "tickets.json"

    def fail(prompt=""):
        raise AssertionError(f"unexpected prompt: {prompt}")

    monkeypatch.setattr("builtins.input", fail)

    code = main([
        "--file", str(path), "create",
        "--title", "Printer broken",
        "--description", "The office printer does not work",
        "--priority", "High",
        "--tags",
    ])

    assert code == 0


def test_create_asks_again_after_an_invalid_answer(tmp_path, capsys, monkeypatch):
    path = tmp_path / "tickets.json"
    answers = iter([
        "Printer broken",
        "The office printer does not work",
        "invalid priority",
        "High",
        "",# no tag
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))

    code = main(["--file", str(path), "create"])

    captured = capsys.readouterr()
    ticket = load_tickets(path).get(captured.out.strip())
    assert code == 0
    assert ticket.priority == "High"
    assert "Priority must be one of" in captured.err


def test_create_asks_again_when_a_given_argument_is_invalid(tmp_path, capsys, monkeypatch):
    path = tmp_path / "tickets.json"
    answers = iter(["High"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))

    code = main([
        "--file", str(path), "create",
        "--title", "Printer broken",
        "--description", "The office printer does not work",
        "--priority", "Urgent",
        "--tags",
    ])

    ticket = load_tickets(path).get(capsys.readouterr().out.strip())
    assert code == 0
    assert ticket.priority == "High"