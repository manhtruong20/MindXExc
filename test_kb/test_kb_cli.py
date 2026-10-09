from kb.cli import main
import pytest
import json

def env_for(tmp_path):
    return {"KB_CLIENT": "mock", "KB_MOCK_FILE": str(tmp_path / "kb.json")}

#retrieve command tests
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


#search command tests
def test_search_lists_matching_documents(tmp_path, capsys):
    code = main(["search", "deployment"], env_for(tmp_path))

    out = capsys.readouterr().out
    assert code == 0
    assert "doc-006" in out
    assert "Deployment Guide" in out
    assert "/docs/guides" in out
    assert "keyword" in out


def test_search_top_k_limits_the_results(tmp_path, capsys):
    main(["search", "email", "--top-k", "1"], env_for(tmp_path))

    out = capsys.readouterr().out
    assert "doc-001" in out
    assert "doc-004" not in out


def test_search_returns_five_results_by_default(tmp_path, capsys):
    main(["search", ""], env_for(tmp_path))

    out = capsys.readouterr().out
    assert "doc-005" in out
    assert "doc-006" not in out


def test_search_without_matches_says_so(tmp_path, capsys):
    code = main(["search", "zzz-no-such-text"], env_for(tmp_path))

    assert code == 0
    assert "No documents found" in capsys.readouterr().out


@pytest.mark.parametrize("value", ["0", "-1", "abc"])
def test_search_rejects_a_bad_top_k(tmp_path, value):
    code = main(["search", "email", "--top-k", value], env_for(tmp_path))

    assert code == 2


def test_search_requires_a_query(tmp_path):
    assert main(["search"], env_for(tmp_path)) == 2


def test_corrupted_data_file_exits_1(tmp_path, capsys):
    path = tmp_path / "kb.json"
    path.write_text("{not json", encoding="utf-8")

    code = main(["retrieve", "doc-001"], {"KB_MOCK_FILE": str(path)})

    assert code == 1
    assert "not valid JSON" in capsys.readouterr().err


#list command tests
def write_documents(tmp_path, count, node="/bulk"):
    records = [
        {
            "id": f"doc-{number:03d}",
            "title": f"Doc {number}",
            "content": "x",
            "node_path": node,
            "tags": [],
        }
        for number in range(1, count + 1)
    ]
    (tmp_path / "kb.json").write_text(json.dumps(records), encoding="utf-8")


def test_list_shows_the_documents_in_a_node(tmp_path, capsys):
    code = main(["list", "--node", "/templates/email"], env_for(tmp_path))

    out = capsys.readouterr().out
    assert code == 0
    assert "doc-001" in out
    assert "doc-004" in out
    assert "doc-002" not in out


def test_list_limit_caps_the_results(tmp_path, capsys):
    main(["list", "--node", "/templates/email", "--limit", "1"], env_for(tmp_path))

    out = capsys.readouterr().out
    assert "doc-001" in out
    assert "doc-004" not in out


def test_list_shows_ten_documents_by_default(tmp_path, capsys):
    write_documents(tmp_path, 11)

    main(["list", "--node", "/bulk"], env_for(tmp_path))

    out = capsys.readouterr().out
    assert "doc-010" in out
    assert "doc-011" not in out


def test_list_of_an_empty_node_says_so(tmp_path, capsys):
    code = main(["list", "--node", "/nowhere"], env_for(tmp_path))

    assert code == 0
    assert "No documents found" in capsys.readouterr().out


@pytest.mark.parametrize("value", ["0", "-1", "abc"])
def test_list_rejects_a_bad_limit(tmp_path, value):
    argv = ["list", "--node", "/templates/email", "--limit", value]

    assert main(argv, env_for(tmp_path)) == 2


def test_list_requires_a_node(tmp_path):
    assert main(["list"], env_for(tmp_path)) == 2


#add command tests
def make_input_file(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_add_stores_the_file_as_a_document(tmp_path, capsys):
    env = env_for(tmp_path)
    path = make_input_file(tmp_path, "welcome-sms.md", "Hello SMS")

    code = main(
        ["add", "--file", str(path), "--path", "/templates/sms", "--tags", "sms,promo"],
        env,
    )

    out = capsys.readouterr().out
    assert code == 0
    assert out.startswith("Added doc-")

    doc_id = out.split()[1]
    assert main(["retrieve", doc_id, "--full"], env) == 0
    retrieved = capsys.readouterr().out
    assert "welcome-sms" in retrieved
    assert "/templates/sms" in retrieved
    assert "tags: sms, promo" in retrieved
    assert "Hello SMS" in retrieved


def test_add_works_without_tags(tmp_path):
    path = make_input_file(tmp_path, "note.md", "text")

    code = main(
        ["add", "--file", str(path), "--path", "/notes"], env_for(tmp_path)
    )

    assert code == 0