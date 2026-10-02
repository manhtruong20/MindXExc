from ticket_manager.cli import main
from ticket_manager.storage import load_tickets

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