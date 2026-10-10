import os, subprocess, sys, re, time
from contextlib import contextmanager

URL_PATTERN = re.compile(r"http://\S+")

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

URL_PATTERN = re.compile(r"http://\S+")

def run_kb_http(url, *args):
    env = {**os.environ, "KB_CLIENT": "http", "KB_API_URL": url}
    return subprocess.run(
        [sys.executable, "-m", "kb", *args],
        capture_output=True,
        text=True,
        input="",
        env=env,
    )


@contextmanager
def fake_server_process(data_file, *options):
    """Start `python -m kb.fake_server` as a real process; yield its URL."""
    process = subprocess.Popen(
        [
            sys.executable, "-m", "kb.fake_server",
            "--port", "0", "--file", str(data_file), *options,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        line = process.stdout.readline()
        match = URL_PATTERN.search(line)
        assert match, f"the server did not start: {line!r} {process.stderr.read()}"
        yield match.group(0)
    finally:
        process.terminate()
        process.wait(timeout=5)
        process.stdout.close()
        process.stderr.close()


def assert_ok(result):
    assert result.returncode == 0, result.stderr


def make_note(tmp_path):
    note = tmp_path / "welcome-sms.md"
    note.write_text("Hello SMS", encoding="utf-8")
    return note


def test_all_four_commands_work_against_a_real_server_process(tmp_path):
    note = make_note(tmp_path)

    with fake_server_process(tmp_path / "server.json") as url:
        retrieved = run_kb_http(url, "retrieve", "doc-001")
        searched = run_kb_http(url, "search", "deployment")
        listed = run_kb_http(url, "list", "--node", "/templates/email")
        added = run_kb_http(
            url, "add", "--file", str(note), "--path", "/templates/sms", "--tags", "sms"
        )
        found = run_kb_http(url, "retrieve", added.stdout.split()[1], "--full")

    for result in (retrieved, searched, listed, added, found):
        assert_ok(result)
    assert "Customer Response Template" in retrieved.stdout
    assert "doc-006  Deployment Guide" in searched.stdout
    assert "doc-004" in listed.stdout
    assert "Hello SMS" in found.stdout


def test_documents_survive_a_server_restart(tmp_path):
    note = make_note(tmp_path)
    data_file = tmp_path / "server.json"

    with fake_server_process(data_file) as url:
        added = run_kb_http(
            url, "add", "--file", str(note), "--path", "/templates/sms", "--tags"
        )
    doc_id = added.stdout.split()[1]

    with fake_server_process(data_file) as new_url:
        found = run_kb_http(new_url, "retrieve", doc_id, "--full")

    assert_ok(added)
    assert_ok(found)
    assert "Hello SMS" in found.stdout


def test_a_server_that_is_not_running_exits_1(dead_url):
    result = run_kb_http(dead_url, "retrieve", "doc-001")

    assert result.returncode == 1
    assert "cannot reach" in result.stderr


def test_the_latency_option_slows_the_answers_down(tmp_path):
    with fake_server_process(tmp_path / "server.json", "--latency", "200", "200") as url:
        started = time.perf_counter()
        result = run_kb_http(url, "retrieve", "doc-001")
        elapsed = time.perf_counter() - started

    assert_ok(result)
    assert elapsed >= 0.15