import subprocess
import sys


def test_cli_runs_as_a_real_process(tmp_path):
    path = tmp_path / "tickets.json"

    result = subprocess.run(
        [sys.executable, "-m", "ticket_manager", "--file", str(path), "list"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "not found" in result.stderr
    assert not path.exists()