import os
import subprocess
import sys


def run_kb(tmp_path, *args):
    env = {
        **os.environ,
        "KB_CLIENT": "mock",
        "KB_MOCK_FILE": str(tmp_path / "kb.json"),
    }
    return subprocess.run(
        [sys.executable, "-m", "kb", *args],
        capture_output=True,
        text=True,
        input="",
        env=env,
    )


def test_python_dash_m_kb_retrieves_a_document(tmp_path):
    result = run_kb(tmp_path, "retrieve", "doc-001")

    assert result.returncode == 0
    assert "Customer Response Template" in result.stdout


def test_a_document_added_by_one_process_is_found_by_the_next(tmp_path):
    note = tmp_path / "welcome-sms.md"
    note.write_text("Hello SMS", encoding="utf-8")

    added = run_kb(
        tmp_path, "add", "--file", str(note), "--path", "/templates/sms", "--tags"
    )
    doc_id = added.stdout.split()[1]
    found = run_kb(tmp_path, "retrieve", doc_id, "--full")

    assert added.returncode == 0
    assert found.returncode == 0
    assert "Hello SMS" in found.stdout


def test_a_bad_command_exits_2(tmp_path):
    assert run_kb(tmp_path, "nonsense").returncode == 2