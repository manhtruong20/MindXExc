from ticket_manager.cli import main
from ticket_manager.storage import load_tickets

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