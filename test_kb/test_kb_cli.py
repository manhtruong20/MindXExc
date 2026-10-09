from kb.cli import main


def env_for(tmp_path):
    return {"KB_CLIENT": "mock", "KB_MOCK_FILE": str(tmp_path / "kb.json")}


def test_retrieve_prints_the_document(tmp_path, capsys):
    code = main(["retrieve", "doc-001"], env_for(tmp_path))

    out = capsys.readouterr().out
    assert code == 0
    assert "Customer Response Template" in out
    assert "/templates/email" in out
    assert "thanks for your message" in out


def test_retrieve_unknown_id_exits_1_with_a_message(tmp_path, capsys):
    code = main(["retrieve", "doc-999"], env_for(tmp_path))

    captured = capsys.readouterr()
    assert code == 1
    assert "doc-999" in captured.err


def test_unknown_kb_client_exits_1_with_a_message(capsys):
    code = main(["retrieve", "doc-001"], {"KB_CLIENT": "carrier-pigeon"})

    captured = capsys.readouterr()
    assert code == 1
    assert "carrier-pigeon" in captured.err


def test_missing_document_id_exits_2(tmp_path, capsys):
    code = main(["retrieve"], env_for(tmp_path))

    assert code == 2


def test_retrieve_shows_only_a_preview_of_long_content(tmp_path, capsys):
    main(["retrieve", "doc-006"], env_for(tmp_path))

    out = capsys.readouterr().out
    assert "2. Deploy to staging" in out
    assert "3. Deploy to production" not in out
    assert "..." in out


def test_retrieve_full_prints_the_whole_content(tmp_path, capsys):
    code = main(["retrieve", "doc-006", "--full"], env_for(tmp_path))

    out = capsys.readouterr().out
    assert code == 0
    assert "3. Deploy to production" in out
    assert "..." not in out


def test_retrieve_help_mentions_the_full_option(capsys):
    code = main(["retrieve", "--help"], {})

    out = capsys.readouterr().out
    assert code == 0
    assert "--full" in out