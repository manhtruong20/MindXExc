from kb.cli import main
import pytest
import json

def env_for(tmp_path):
    return {"KB_CLIENT": "mock", "KB_MOCK_FILE": str(tmp_path / "kb.json")}

def type_answers(monkeypatch, *answers):
    replies = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(replies))


def no_input(monkeypatch):
    def raise_eof(prompt=""):
        raise EOFError

    monkeypatch.setattr("builtins.input", raise_eof)


def retrieve_added(out, env, capsys):
    doc_id = out.split()[1]
    main(["retrieve", doc_id, "--full"], env)
    return capsys.readouterr().out

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
        ["add", "--file", str(path), "--path", "/templates/sms", "--tags", "sms promo"],
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


def test_add_with_a_missing_file_exits_1(tmp_path, capsys, monkeypatch):
    no_input(monkeypatch)
    missing = tmp_path / "missing.md"

    code = main(["add", "--file", str(missing), "--path", "/x"], env_for(tmp_path))

    assert code == 1
    assert "missing.md" in capsys.readouterr().err


def test_add_with_a_file_that_is_not_text_exits_1(tmp_path, capsys, monkeypatch):
    no_input(monkeypatch)
    path = tmp_path / "binary.bin"
    path.write_bytes(b"\xff\xfe\x00\xff")

    code = main(["add", "--file", str(path), "--path", "/x"], env_for(tmp_path))

    assert code == 1
    assert "binary.bin" in capsys.readouterr().err


def test_add_splits_tags_on_whitespace_and_drops_duplicates(tmp_path, capsys):
    env = env_for(tmp_path)
    path = make_input_file(tmp_path, "note.md", "text")

    main(
        ["add", "--file", str(path), "--path", "/n", "--tags", "sms", "promo sale", "sms"],
        env,
    )
    doc_id = capsys.readouterr().out.split()[1]
    main(["retrieve", doc_id], env)

    assert "tags: sms, promo, sale\n" in capsys.readouterr().out


def test_add_accepts_tags_with_no_values(tmp_path, capsys):
    env = env_for(tmp_path)
    path = make_input_file(tmp_path, "note.md", "text")

    code = main(["add", "--file", str(path), "--path", "/n", "--tags"], env)
    doc_id = capsys.readouterr().out.split()[1]
    main(["retrieve", doc_id], env)

    assert code == 0
    assert "tags: \n" in capsys.readouterr().out


def test_add_asks_for_a_missing_file(tmp_path, capsys, monkeypatch):
    path = make_input_file(tmp_path, "note.md", "text")
    type_answers(monkeypatch, str(path))

    code = main(["add", "--path", "/n", "--tags"], env_for(tmp_path))

    assert code == 0
    assert capsys.readouterr().out.startswith("Added doc-")


def test_add_asks_again_when_a_given_file_cannot_be_read(tmp_path, capsys, monkeypatch):
    good = make_input_file(tmp_path, "note.md", "text")
    type_answers(monkeypatch, str(good))
    missing = tmp_path / "missing.md"

    code = main(
        ["add", "--file", str(missing), "--path", "/n", "--tags"], env_for(tmp_path)
    )

    captured = capsys.readouterr()
    assert code == 0
    assert "Invalid file" in captured.err
    assert captured.out.startswith("Added doc-")


def test_add_asks_for_a_missing_node_path(tmp_path, capsys, monkeypatch):
    env = env_for(tmp_path)
    path = make_input_file(tmp_path, "note.md", "text")
    type_answers(monkeypatch, "/templates/sms")

    main(["add", "--file", str(path), "--tags"], env)

    out = retrieve_added(capsys.readouterr().out, env, capsys)
    assert "node: /templates/sms" in out


def test_add_asks_again_when_the_node_path_is_blank(tmp_path, capsys, monkeypatch):
    path = make_input_file(tmp_path, "note.md", "text")
    type_answers(monkeypatch, "", "/n")

    code = main(["add", "--file", str(path), "--tags"], env_for(tmp_path))

    captured = capsys.readouterr()
    assert code == 0
    assert "Invalid path" in captured.err


def test_add_asks_for_tags_and_an_empty_answer_means_none(tmp_path, capsys, monkeypatch):
    env = env_for(tmp_path)
    path = make_input_file(tmp_path, "note.md", "text")
    type_answers(monkeypatch, "")

    code = main(["add", "--file", str(path), "--path", "/n"], env)

    assert code == 0
    assert "tags: \n" in retrieve_added(capsys.readouterr().out, env, capsys)


def test_add_splits_the_typed_tags(tmp_path, capsys, monkeypatch):
    env = env_for(tmp_path)
    path = make_input_file(tmp_path, "note.md", "text")
    type_answers(monkeypatch, "sms promo")

    main(["add", "--file", str(path), "--path", "/n"], env)

    assert "tags: sms, promo\n" in retrieve_added(capsys.readouterr().out, env, capsys)


def test_add_asks_again_when_tags_are_invalid(tmp_path, capsys, monkeypatch):
    env = env_for(tmp_path)
    path = make_input_file(tmp_path, "note.md", "text")
    type_answers(monkeypatch, "-urgent", "urgent")

    code = main(["add", "--file", str(path), "--path", "/n"], env)

    captured = capsys.readouterr()
    assert code == 0
    assert "Invalid tags" in captured.err
    assert "tags: urgent\n" in retrieve_added(captured.out, env, capsys)


def test_add_asks_again_when_a_dash_tag_is_given_with_equals(tmp_path, capsys, monkeypatch):
    env = env_for(tmp_path)
    path = make_input_file(tmp_path, "note.md", "text")
    type_answers(monkeypatch, "urgent")

    main(["add", "--file", str(path), "--path", "/n", "--tags=-urgent"], env)

    assert "tags: urgent\n" in retrieve_added(capsys.readouterr().out, env, capsys)


def test_add_without_any_input_exits_1(tmp_path, capsys, monkeypatch):
    no_input(monkeypatch)

    code = main(["add"], env_for(tmp_path))

    assert code == 1
    assert "no input available" in capsys.readouterr().err


#test KB CLI works over HTTP
def http_env(url):
    return {"KB_CLIENT": "http", "KB_API_URL": url}


def argv_for(name, tmp_path):
    note = tmp_path / "note.md"
    note.write_text("text", encoding="utf-8")
    return {
        "retrieve": ["retrieve", "doc-001"],
        "search": ["search", "email"],
        "list": ["list", "--node", "/x"],
        "add": ["add", "--file", str(note), "--path", "/x", "--tags"],
    }[name]


@pytest.mark.parametrize("name", ["retrieve", "search", "list", "add"])
def test_an_unreachable_server_exits_1_with_a_message(name, tmp_path, capsys, dead_url):
    code = main(argv_for(name, tmp_path), http_env(dead_url))

    assert code == 1
    assert "cannot reach" in capsys.readouterr().err


def test_http_without_an_address_exits_1(capsys):
    code = main(["retrieve", "doc-001"], {"KB_CLIENT": "http"})

    assert code == 1
    assert "KB_API_URL" in capsys.readouterr().err


def test_all_four_commands_work_through_the_http_client(server_url, tmp_path, capsys):
    env = http_env(server_url)

    assert main(["retrieve", "doc-001"], env) == 0
    assert "Customer Response Template" in capsys.readouterr().out

    assert main(["search", "deployment"], env) == 0
    assert "doc-006  Deployment Guide  /docs/guides  [keyword]" in capsys.readouterr().out

    assert main(["list", "--node", "/templates/email"], env) == 0
    assert "doc-004" in capsys.readouterr().out

    note = tmp_path / "welcome-sms.md"
    note.write_text("Hello SMS", encoding="utf-8")
    assert main(["add", "--file", str(note), "--path", "/templates/sms", "--tags", "sms"], env) == 0
    doc_id = capsys.readouterr().out.split()[1]
    assert main(["retrieve", doc_id, "--full"], env) == 0
    assert "Hello SMS" in capsys.readouterr().out